import os
import logging
import sqlite3
from datetime import datetime
import qrcode
from nfc_reader import NFCReader

# Configure main logging
logging.basicConfig(level=logging.DEBUG)

# Configure logging for station2.log
log_file_path = "station2.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

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
        logging.info("Initializing RFID reader and database connection...")
        try:
            self.machine.nfc_reader = NFCReader()
            if self.machine.connect_db():
                logging.info("Initialization successful")
                self.machine.current_state = 'State1'
            else:
                raise Exception("Database connection failed")
        except Exception as e:
            logging.error(f"Initialization failed: {e}")
            self.machine.current_state = 'State5'

class State1(State):
    def run(self):
        logging.info("Waiting for RFID card...")
        try:
            self.machine.uid = bytes(self.machine.nfc_reader.read_passive_target(timeout=10))
            if self.machine.uid:
                logging.info(f"Card detected: {[hex(i) for i in self.machine.uid]}")
                self.machine.current_state = 'State2'
            else:
                self.machine.current_state = 'State1'
        except Exception as e:
            logging.error(f"Card reading error: {e}")
            self.machine.current_state = 'State5'

class State2(State):
    def run(self):
        logging.info("Checking if the RFID chip is already tagged...")
        try:
            cursor = self.machine.conn.cursor()

            cursor.execute('''
                SELECT Flaschen_ID, Tagged_Date 
                FROM Flasche 
                WHERE Flaschen_ID = ? AND Tagged_Date != 0
            ''', (self.machine.bottle_id,))
            result = cursor.fetchone()

            if result:
                logging.info(f"Bottle ID {result[0]} already tagged on {result[1]}")
                self.machine.current_state = 'State1'
                return

            cursor.execute('''
                SELECT Flaschen_ID
                FROM Flasche 
                WHERE Tagged_Date = 0
                LIMIT 1
            ''')
            result = cursor.fetchone()

            if not result:
                logging.error("No available bottles found")
                self.machine.current_state = 'State5'
                return

            self.machine.bottle_id = result[0]

            block_number = 2
            data = self.machine.bottle_id.to_bytes(16, byteorder='big')
            if self.machine.nfc_reader.write_block(self.machine.uid, block_number, data):
                logging.info(f"Bottle ID {self.machine.bottle_id} written to RFID chip.")
                self.machine.current_state = 'State3'
            else:
                raise Exception("Failed to write Bottle ID to RFID chip")
                
        except Exception as e:
            logging.error(f"Error during bottle tagging process: {e}")
            self.machine.current_state = 'State1'

class State3(State):
    def run(self):
        logging.info("Updating database...")
        try:
            cursor = self.machine.conn.cursor()
            timestamp = int(datetime.now().timestamp())
            cursor.execute('''
                UPDATE Flasche 
                SET Tagged_Date = ?, has_error = ?
                WHERE Flaschen_ID = ?
            ''', (timestamp, False, self.machine.bottle_id))
            self.machine.conn.commit()
            self.machine.recipe = self.get_recipe(cursor)
            self.machine.current_state = 'State4'
        except Exception as e:
            logging.error(f"Database update failed: {e}")
            self.machine.current_state = 'State5'

    def get_recipe(self, cursor):
        logging.info("Fetching recipe details...")
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
        logging.info("Outputting recipe information and generating QR code...")
        try:
            # Log and print the recipe
            bottle_log = f"Filling details for Bottle ID: {self.machine.bottle_id}\n"
            for granule_id, quantity in self.machine.recipe:
                log_message = f"Granule ID: {granule_id}, Quantity: {quantity}"
                logging.info(log_message)
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
            logging.info(f"QR code generated and saved at {qr_file_path}")

            bottle_log += f"QR Code saved at: {qr_file_path}\n"
            bottle_log += "-" * 40 + "\n"

            with open(log_file_path, "a") as log_file:
                log_file.write(bottle_log)

            self.machine.current_state = 'State1'

        except Exception as e:
            logging.error(f"Error during QR code generation: {e}")
            self.machine.current_state = 'State5'

class State5(State):
    def run(self):
        logging.error("Process failed - check logs")
        self.machine.current_state = 'State5'

if __name__ == '__main__':
    DB_PATH = "/home/maxsim/maxsim-NFC-raspi/data/flaschen_database.db"
    machine = StateMachine(DB_PATH)
    machine.run()
