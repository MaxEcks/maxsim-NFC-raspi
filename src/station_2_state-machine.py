import os
import logging
import sqlite3
from datetime import datetime
import qrcode
from nfc_reader import NFCReader
import time

# Configure the main logger
logging.basicConfig(level=logging.DEBUG)

# Directory and file paths for logs
log_directory = "/home/maxsim/maxsim-NFC-raspi/logging"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file_path = os.path.join(log_directory, "station2.log")

# Configure a separate logger for station2.log
station2_logger = logging.getLogger("Station2Logger")
station2_handler = logging.FileHandler(log_file_path)
station2_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
station2_handler.setFormatter(station2_formatter)
station2_logger.addHandler(station2_handler)
station2_logger.setLevel(logging.DEBUG)

class StateMachine:
    def __init__(self, db_path):
        self.current_state = 'State0'
        self.nfc_reader = None
        self.uid = None
        self.bottle_id = None
        self.recipe = []
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
            station2_logger.error(f"Database connection error: {e}")
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
        station2_logger.info("Initializing RFID reader and database connection...")
        try:
            self.machine.nfc_reader = NFCReader()
            if self.machine.connect_db():
                station2_logger.info("Initialization successful")
                self.machine.current_state = 'State1'
            else:
                raise Exception("Database connection failed")
        except Exception as e:
            station2_logger.error(f"Initialization failed: {e}")
            self.machine.current_state = 'State5'

class State1(State):
    def run(self):
        station2_logger.info("Waiting for RFID card...")
        try:
            self.machine.uid = self.machine.nfc_reader.read_passive_target(timeout=10)
            if self.machine.uid:
                self.machine.uid = bytes(self.machine.uid)
                station2_logger.info(f"Card detected: {[hex(i) for i in self.machine.uid]}")
                self.machine.current_state = 'State2'
                time.sleep(1)  # Add a 1-second wait
            else:
                raise Exception("Timeout occurred while waiting for RFID card.")
        except Exception as e:
            station2_logger.error(f"Card reading error: {e}")
            self.machine.current_state = 'State5'

class State2(State):
    def run(self):
        station2_logger.info("Fetching bottle information from RFID chip...")
        try:
            block_number = 2
            data = self.machine.nfc_reader.read_block(self.machine.uid, block_number)
            if data and any(data):
                self.machine.bottle_id = int.from_bytes(data, byteorder='big')
                station2_logger.info(f"Bottle ID {self.machine.bottle_id} read from RFID chip.")
                self.machine.current_state = 'State3'
            else:
                station2_logger.error("No valid Bottle ID found on RFID chip")
                self.machine.current_state = 'State5'
        except Exception as e:
            station2_logger.error(f"Error reading Bottle ID from RFID chip: {e}")
            self.machine.current_state = 'State5'

class State3(State):
    def run(self):
        station2_logger.info("Fetching recipe details from the database...")
        try:
            cursor = self.machine.conn.cursor()
            self.machine.recipe = self.get_recipe(cursor)
            if self.machine.recipe:
                self.machine.current_state = 'State4'
            else:
                station2_logger.error(f"No recipe found for Bottle ID {self.machine.bottle_id}")
                self.machine.current_state = 'State5'
        except Exception as e:
            station2_logger.error(f"Database query failed: {e}")
            self.machine.current_state = 'State5'

    def get_recipe(self, cursor):
        station2_logger.info(f"Fetching recipe for Bottle ID {self.machine.bottle_id}...")
        cursor.execute('''
            SELECT Granulat_ID, Menge 
            FROM Rezept_besteht_aus_Granulat 
            WHERE Rezept_ID = (
                SELECT Rezept_ID 
                FROM Flasche 
                WHERE Flaschen_ID = ?
            )
        ''', (self.machine.bottle_id,))
        return cursor.fetchall()

class State4(State):
    def run(self):
        station2_logger.info("Outputting recipe information and generating QR code...")
        try:
            # Log and print the recipe
            bottle_log = f"Filling details for Bottle ID: {self.machine.bottle_id}\n"
            for granule_id, quantity in self.machine.recipe:
                log_message = f"Granule ID: {granule_id}, Quantity: {quantity}"
                station2_logger.info(log_message)
                bottle_log += log_message + "\n"
                print(log_message)

            # Fetch the Recipe ID and generate a QR code
            cursor = self.machine.conn.cursor()
            cursor.execute('''
                SELECT f.Rezept_ID 
                FROM Flasche f 
                WHERE f.Flaschen_ID = ?
            ''', (self.machine.bottle_id,))
            result = cursor.fetchone()

            if not result:
                raise Exception(f"No Recipe ID found for Bottle ID {self.machine.bottle_id}")
            
            recipe_id = result[0]
            date = int(datetime.now().timestamp())

            # Create the QR code content
            qr_content = f"Flaschen_ID: {self.machine.bottle_id}, Rezept_ID: {recipe_id}, Date: {date}"
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(qr_content)
            qr.make(fit=True)

            qr_directory = "qr_codes"
            os.makedirs(qr_directory, exist_ok=True)
            qr_file_path = os.path.join(qr_directory, f"qr_bottle_{self.machine.bottle_id}.png")
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image.save(qr_file_path)
            station2_logger.info(f"QR code generated and saved at {qr_file_path}")

            bottle_log += f"QR Code saved at: {qr_file_path}\n"
            bottle_log += "-" * 40 + "\n"

            with open(log_file_path, "a") as log_file:
                log_file.write(bottle_log)

            self.machine.current_state = 'State1'
            time.sleep(2)  # Add a 2-second wait

        except Exception as e:
            station2_logger.error(f"Error during QR code generation: {e}")
            self.machine.current_state = 'State5'

class State5(State):
    def run(self):
        station2_logger.error("Process failed - check logs")
        print("Process failed at some point. Please check the logs.")  # Print to terminal
        self.machine.current_state = 'State5'  # End of process

if __name__ == '__main__':
    DB_PATH = "/home/maxsim/maxsim-NFC-raspi/data/flaschen_database.db"
    machine = StateMachine(DB_PATH)
    machine.run()