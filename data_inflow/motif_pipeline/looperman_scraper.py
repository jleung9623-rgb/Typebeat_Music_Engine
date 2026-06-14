import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database.models import SectionClass, TrackClass

class LoopermanMIDIScraper:
    def __init__(self, motif_dir="data_inflow/motif_pipeline", csv_dir="data_inflow/motif_pipeline"):
        self.motif_dir = motif_dir
        self.csv_path = os.path.join(csv_dir, "tracks_payload.csv")
        os.makedirs(self.motif_dir, exist_ok=True)
        os.makedirs(csv_dir, exist_ok=True)

        # Initialize the CSV Payload header if the file does not exist
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w') as f:
                f.write("track_name,track_class,genre_name,midi_channel,scale_name,instrument_name\n")

        # Headless Configuration
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

        # The Heuristic Routing Map
        # Maps substrings found in the URL slug to the strict database Enums
        self.slug_router = {
            "hook": SectionClass.CHORUS.name,
            "chorus": SectionClass.CHORUS.name,
            "drop": SectionClass.CHORUS.name,
            "verse": SectionClass.VERSE.name,
            "intro": SectionClass.OPENING.name,
            "bridge": SectionClass.BRIDGE.name,
            "build": SectionClass.BUILD.name
        }

        self.track_router = {
            "guitar acoustic": TrackClass.MELODIC_LEAD,
            "guitar electric": TrackClass.MELODIC_LEAD,
            "rhodes piano": TrackClass.MELODIC_LEAD,
            "bass wobble": TrackClass.BASS,
            "bass guitar": TrackClass.BASS,
            "bass synth": TrackClass.BASS,
            "soundscapes": TrackClass.PAD_ATMOSPHERE,
            "harpsichord": TrackClass.MELODIC_LEAD,
            "percussion": TrackClass.PERCUSSION,
            "didgeridoo": TrackClass.PAD_ATMOSPHERE,
            "orchestral": TrackClass.PAD_ATMOSPHERE,
            "accordion": TrackClass.MELODIC_LEAD,
            "arpeggio": TrackClass.MELODIC_LEAD,
            "clarinet": TrackClass.MELODIC_LEAD,
            "woodwind": TrackClass.MELODIC_LEAD,
            "bagpipe": TrackClass.MELODIC_LEAD,
            "beatbox": TrackClass.PERCUSSION,
            "strings": TrackClass.PAD_ATMOSPHERE,
            "scratch": TrackClass.FX,
            "ukulele": TrackClass.MELODIC_LEAD,
            "groove": TrackClass.PERCUSSION,
            "choir": TrackClass.PAD_ATMOSPHERE,
            "banjo": TrackClass.MELODIC_LEAD,
            "bells": TrackClass.MELODIC_LEAD,
            "brass": TrackClass.MELODIC_LEAD,
            "flute": TrackClass.MELODIC_LEAD,
            "organ": TrackClass.PAD_ATMOSPHERE,
            "piano": TrackClass.MELODIC_LEAD,
            "sitar": TrackClass.MELODIC_LEAD,
            "synth": TrackClass.MELODIC_LEAD,
            "tabla": TrackClass.PERCUSSION,
            "vocal": TrackClass.MELODIC_LEAD,
            "bass": TrackClass.BASS,
            "drum": TrackClass.PERCUSSION,
            "harp": TrackClass.MELODIC_LEAD,
            "pad": TrackClass.PAD_ATMOSPHERE,
            "fx": TrackClass.FX
        }

        # We need to align this logic later on with the MIDI Extractor

    def get_requests_session(self):
        """Transfers authenticated Selenium cookies to a requests session."""
        session = requests.Session()
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        # Inherits the exact User-Agent to prevent bot-flagging
        session.headers.update({"User-Agent": self.driver.execute_script("return navigator.userAgent;")})

        return session

    def extract_metadata(self, container_element):
        """Parses the DOM container to extract the ID, Slug, and Binary URL."""
        try:
            # Extracts the Title Anchor to get the slug
            title_element = container_element.find_element(By.XPATH, ".//a[contains(@class, 'player-title')]")
            full_url = title_element.get_attribute("href")
            slug = full_url.split('/')[-1].lower()
            loop_id = full_url.split('/')[-2]
            
            # Extracts the hash directly from the parent wrapper and constructs the URL
            data_hash = container_element.get_attribute("data-hash")
            if not data_hash:
                raise ValueError("data-hash attribute missing from player-wrapper")
            
            download_url = f"https://www.looperman.com/getfiles/loops/{data_hash}"

            return loop_id, slug, download_url
        
        except Exception as e:
            print(f"DOM parsing failure on container: {e}")
            return None, None, None
        
    def route_section_class(self, slug):
        """Evaluates the URL slug against the routing dictionary."""
        for keyword, section_enum in self.slug_router.items():
            if keyword in slug:
                return section_enum
        
        # Mathematical default if no structural intent is defined
        return SectionClass.VERSE.name
    
    def route_track_class(self, slug):
        """Evaluates the URL slug to extract sound qualities and functional track class."""
        # Converts slug hyphens to spaces to match multi-word keys like "bass guitar"
        normalized_slug = slug.replace("-", " ")

        for keyword, track_enum in self.track_router.items():
            if keyword in normalized_slug:
                return track_enum.name, keyword
        
        # Mathematical fallback
        return TrackClass.MELODIC_LEAD.name, "unknown"
    
    def log_track_csv(self, loop_id, track_class, instrument_name):
        """Appends the dynamically extracted track metadata to the SQL payload file."""
        track_name = f"Looperman_{loop_id}"

        # Note: genre, midi_channel, and scale are passed as static placeholders.
        # The switchboard requires them, but they can be manually bulk-updated in the CSV later if needed
        row = f"{track_name},{track_class},Trap,1,C_Major,{instrument_name}\n"

        with open(self.csv_path, 'a') as f:
            f.write(row)
    
    def intercept_and_download(self, download_url, loop_id, slug):
        """Bypass Selenium UI downloading to strictly control the file write."""
        req_session = self.get_requests_session()

        # Executes the binary stream
        response = req_session.get(download_url, stream=True)
        
        if response.status_code == 200:
            # Implements routing logic
            section_class = self.route_section_class(slug)
            track_class, instrument_name = self.route_track_class(slug)

            # Enforces the strict Regex gatekeeper format required by midi_extractor.py
            safe_filename = f"Looperman_{loop_id}-{section_class}.mid"
            file_path = os.path.join(self.motif_dir, safe_filename)

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Logs the data matrix
            self.log_track_csv(loop_id, track_class, instrument_name)

            print(f"Successfully intercepted and saved {safe_filename}.")
            return True
        else:
            print(f"ERROR: Server rejected binary request. Status {response.status_code}")
            return False

    def execute_scrape(self, target_url):
        """Main execution loop."""
        print(f"--- Booting Headless Extraction Sequence ---")
        self.driver.get(target_url)

        # Wait for the DOM to render the player wrappers
        containers = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'player-wrapper')]")))
        print(f"Identified {len(containers)} loop containers on target page.")

        for container in containers:
            loop_id, slug, download_url = self.extract_metadata(container)

            if loop_id and download_url:
                self.intercept_and_download(download_url, loop_id, slug)

                # Enforce a randomized delay to prevent rate-limiting bans
                time.sleep(2)

    def teardown(self):
        self.driver.quit()

if __name__ == "__main__":
    scraper = LoopermanMIDIScraper()
    try:
        # Note: You MUST provide a URL that explicitly filters for MIDI files.
        # For example, "https://www.looperman.com/loops?page=2"
        scraper.execute_scrape("https://www.looperman.com/loops/tags/free-midi-loops-samples-sounds-wavs-download")
    finally:
        scraper.teardown()