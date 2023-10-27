import json
import os


class CSVParser:
    target_dir = "data/"
    limiter = ";"
    result_file = "result.csv"
    headers = [
                "title", "title_search", "title_keyword", "url", 
                "summary", "genre", "metascore", "critic_reviews", 
                "user_score", "user_reviews", "release_date", "images", 
                "video", "video_type", "sentiment", "must_play", "crew",
                "countries", "companies", "platforms", "rating", "official_site"
            ]
    
    def __init__(self):
        self.transform()

    def write_data(self, text):
        with open(os.path.join(self.target_dir, self.result_file), 'a+', encoding='utf-8') as f:
            f.write(text)

    def value_parser(self, value):
        if isinstance(value, int):
            return str(value).replace("\n", "").replace("\r", "")
        elif isinstance(value, str):
            return "\""+value.replace("\n", "").replace("\r", "").replace("\"", "")+"\""
        else:
            return ""
    
    def transform(self):
        file_path = os.path.join(self.target_dir, self.result_file)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Write headers
        line_headers = ""
        for header in self.headers:
            line_headers += header + self.limiter
        self.write_data(line_headers[:-1] + "\n")

        # Transform the json data into CSV file
        for file in os.listdir(self.target_dir):
            if file[-4:] == "json":
                with open(os.path.join(self.target_dir, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for obj in data:
                    dat = json.loads(obj)
                    line = ""
                    for header in self.headers:
                        if isinstance(dat[header], list):
                            array_data = ""
                            for i in range(0, len(dat[header])):
                                array_data = str(dat[header][i] + ",")
                            line += self.value_parser(array_data[:-1]) + self.limiter
                        else:
                            line += self.value_parser(dat[header]) + self.limiter
                    if len(line) > 0:
                        text = line[:-1] + "\n"
                        self.write_data(text)