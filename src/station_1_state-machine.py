import logging
import os
import sqlite3
from datetime import datetime
from nfc_reader import NFCReader
import time # Add time module for sleep function

# Configure the main logger
logging.basicConfig(level=logging.DEBUG)

log_directory = "/home/maxsim/maxsim-NFC-raspi/logging"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file_path = os.path.join(log_directory, "station1.log")

# Configure a separate logger for station1.log
station1_logger = logging.getLogger("Station1Logger")
station1_handler = logging.FileHandler(log_file_path)
station1_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
station1_handler.setFormatter(station1_formatter)
station1_logger.addHandler(station1_handler)
station1_logger.setLevel(logging.DEBUG)

class StateMachine:
    def __init__(self, db_path):
        self.current_state = 'State0'
        self.nfc_reader = None
        self.uid = None
        self.bottle_id = None
        self.db_path = db_path
        self.conn = None
        self.states = {
            'State0': State0(self),
            'State1': State1(self),
            'State2': State2(self),
            'State3': State3(self),
            'State4': State4(self),
            'State5': State5(self)
        }

    def connect_db(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            return True
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            return False

    def close_db(self):
        if self.conn:
            self.conn.close()

    def run(self):
        try:
            while self.current_state not in ['State5']:
                state = self.states[self.current_state]
                state.run()
        finally:
            self.close_db()

class State:
    def __init__(self, machine):
        self.machine = machine

    def run(self):
        raise NotImplementedError

class State0(State):
    def run(self):
        station1_logger.info("Initializing RFID reader and database connection...")
        try:
            self.machine.nfc_reader = NFCReader()   # Initialize the NFC reader
            if self.machine.connect_db():   # Connect to the database
                station1_logger.info("Initialization successful")
                self.machine.current_state = 'State1'
            else:
                raise Exception("Database connection failed")
        except Exception as e:
            station1_logger.error(f"Initialization failed: {e}")
            self.machine.current_state = 'State5'

class State1(State):
    def run(self):
        logging.info("Waiting for RFID card...")
        try:
            uid = self.machine.nfc_reader.read_passive_target(timeout=10)
            if uid is None:
                raise Exception("Timeout occurred while waiting for RFID card.")
            self.machine.uid = bytes(uid)  # Convert to bytes only if uid is not None
            logging.info(f"Card detected: {[hex(i) for i in self.machine.uid]}")
            self.machine.current_state = 'State2'
            time.sleep(1)  # Add a 1-second wait
        except Exception as e:
            logging.error(f"Card reading error: {e}")
            station1_logger.error(f"Card reading error: {e}")  # Log to station1.log
            print(f"Card reading error: {e}")  # Print to terminal
            self.machine.current_state = 'State5'  # Transition to State5

class State2(State):
    def run(self):
        logging.info("Checking if the RFID chip is already tagged...")
        try:
            block_number = 2
            data = self.machine.nfc_reader.read_block(self.machine.uid, block_number)
            if data and any(data):
                self.machine.bottle_id = int.from_bytes(data, byteorder='big')
                cursor = self.machine.conn.cursor()
                cursor.execute('''
                    SELECT Flaschen_ID, Tagged_Date 
                    FROM Flasche 
                    WHERE Flaschen_ID = ? AND Tagged_Date != 0
                ''', (self.machine.bottle_id,))
                result = cursor.fetchone()

                if result:
                    logging.info(f"Bottle ID {result[0]} already tagged on {result[1]}")
                    time.sleep(2)  # Add a 2-second wait before retrying
                    self.machine.current_state = 'State1'  # Return to waiting for new RFID
                    return
                else:
                    logging.info(f"Bottle ID {self.machine.bottle_id} found in block but not tagged in database")
                    self.machine.current_state = 'State3'
            else:
                logging.info("Block 2 is empty, fetching an untagged bottle ID...")
                cursor = self.machine.conn.cursor()
                cursor.execute('''
                    SELECT Flaschen_ID
                    FROM Flasche 
                    WHERE Tagged_Date = 0
                    LIMIT 1
                ''')
                result = cursor.fetchone()

                if not result:
                    station1_logger.error("No available bottles found")
                    self.machine.current_state = 'State5'
                    return

                self.machine.bottle_id = result[0]
                data = self.machine.bottle_id.to_bytes(16, byteorder='big')
                if self.machine.nfc_reader.write_block(self.machine.uid, block_number, data):
                    station1_logger.info(f"Bottle ID {self.machine.bottle_id} written to RFID chip.")
                    self.machine.current_state = 'State3'
                else:
                    raise Exception("Failed to write Bottle ID to RFID chip")

        except Exception as e:
                station1_logger.error(f"Error during bottle tagging process: {e}")
                self.machine.current_state = 'State1'

class State3(State):
    def run(self):
        logging.info("Updating database...")
        try:
            cursor = self.machine.conn.cursor()
            # Get current Unix timestamp (seconds since epoch)
            unix_timestamp = str(int(time.time()))

            cursor.execute('''
                UPDATE Flasche 
                SET Tagged_Date = ?, has_error = ?
                WHERE Flaschen_ID = ?
            ''', (unix_timestamp, False, self.machine.bottle_id))
            self.machine.conn.commit()

            # Log filling quantities to station1.log
            station1_logger.info(f"Bottle ID: {self.machine.bottle_id} tagged successfully.")
            station1_logger.info(f"Timestamp: {unix_timestamp}")

            self.machine.current_state = 'State4'
        except Exception as e:
            station1_logger.error(f"Database update failed: {e}")
            self.machine.current_state = 'State5'

class State4(State):
    def run(self):
        logging.info("Process completed for one bottle, proceeding to next...")
        time.sleep(2)  # Add a 2-second wait before restarting the process
        self.machine.current_state = 'State1'

class State5(State):
    def run(self):
        logging.error("Process failed at some point. Please check the logs.")
        logging.info("Entering State5: Process failed or stopped.")
        station1_logger.error("Process failed at some point. Please check the logs.")  # Log to station1.log
        print("Process failed at some point. Please check the logs.")  # Print to terminal
        self.machine.current_state = 'State5'  # End of process

if __name__ == "__main__":
    DB_PATH = "/home/maxsim/maxsim-NFC-raspi/data/flaschen_database.db"
    machine = StateMachine(DB_PATH)
    machine.run()