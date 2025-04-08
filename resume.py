import requests
import argparse
from fpdf import FPDF

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def fetch_resume(name):
    url = f"https://expressjs-api-resume-random.onrender.com/resume?name={name}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

class ResumePDF(FPDF):
    def __init__(self, font_color, font_size, bg_color):
        super().__init__()
        self.font_color = font_color
        self.font_size = font_size
        self.bg_color = bg_color
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(15, 15, 15)
        self.set_fill_color(*self.bg_color)
        self.rect(0, 0, self.w, self.h, 'F')

    def draw_separator(self):
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

    def header_info(self, data):
        self.set_text_color(*self.font_color)
        self.set_font("Arial", "B", self.font_size + 4)
        self.cell(0, 10, data.get("name", ""), ln=True)

        self.set_font("Arial", "", self.font_size)
        contact = f"{data.get('email', '')} | {data.get('phone', '')} | {data.get('twitter', '')}"
        self.cell(0, 8, contact, ln=True)
        self.cell(0, 8, data.get("address", ""), ln=True)
        self.ln(6)
        self.draw_separator()

    def add_section(self, title, content):
        self.set_text_color(*self.font_color)

        # Section Heading
        self.set_font("Arial", "B", self.font_size + 8)
        self.cell(0, 10, title, ln=True)

        # Section Content
        self.set_font("Arial", "", self.font_size+5)

        if isinstance(content, str):
            self.multi_cell(0, self.font_size + 2, content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, str):
                    self.cell(5)  # indent
                    self.cell(0, self.font_size + 2, f"- {item}", ln=True)
                elif isinstance(item, dict):
                    self.set_font("Arial", "B", self.font_size + 4)
                    self.cell(0, self.font_size + 4, item.get("title", ""), ln=True)

                    self.set_font("Arial", "", self.font_size+6)
                    self.multi_cell(0, self.font_size + 2, f"    {item.get('description', '')}")

                    duration = f"{item.get('startDate', '')} to {item.get('endDate', '')}"
                    self.cell(0, self.font_size + 2, f"    Duration: {duration}", ln=True)
                    self.ln(4)

        self.ln(2)
        self.draw_separator()


def generate_pdf(data, font_size, font_color, bg_color):
    font_rgb = hex_to_rgb(font_color)
    bg_rgb = hex_to_rgb(bg_color)
    pdf = ResumePDF(font_rgb, font_size, bg_rgb)

    pdf.header_info(data)
    pdf.add_section("Summary", data.get("summary", ""))
    pdf.add_section("Skills", data.get("skills", []))
    pdf.add_section("Projects", data.get("projects", []))

    filename = f"{data.get('name', 'resume').replace(' ', '_')}_resume.pdf"
    pdf.output(filename)
    print(f"✅ Resume saved as '{filename}'")

def main():
    parser = argparse.ArgumentParser(description="Generate a customizable resume PDF from API.")
    parser.add_argument("--name", required=True, help="Name to fetch resume from API")
    parser.add_argument("--font-size", type=int, default=12, help="Font size for all text")
    parser.add_argument("--font-color", default="#000000", help="Font color (hex)")
    parser.add_argument("--background-color", default="#FFFFFF", help="Background color (hex)")

    args = parser.parse_args()
    resume_data = fetch_resume(args.name)
    generate_pdf(resume_data, args.font_size, args.font_color, args.background_color)

if __name__ == "__main__":
    main()
