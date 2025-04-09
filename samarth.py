import argparse
import requests
from fpdf import FPDF
from matplotlib.colors import to_rgb


def convert_color(color):
    try:
        r, g, b = to_rgb(color)
        return int(r * 255), int(g * 255), int(b * 255)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid color format: {color}")


def get_resume_data(candidate_name):
    api_url = f"https://expressjs-api-resume-random.onrender.com/resume?name={candidate_name}"
    response = requests.get(api_url)
    if response.ok:
        return response.json()
    raise RuntimeError(f"Could not retrieve resume for: {candidate_name}")


class PDFResume(FPDF):
    def __init__(self, size, color, bg_color):
        super().__init__()
        self.font_size = size
        self.font_color = color
        self.bg_color = bg_color
        self.add_page()
        self.set_auto_page_break(True, margin=15)
        self.set_fill_color(*bg_color)
        self.set_text_color(*color)
        self.set_font("Arial", size=size)

    def add_separator(self):
        self.set_draw_color(*self.font_color)
        y = self.get_y()
        self.line(10, y, 200, y)
        self.ln(5)

    def add_header(self, name, contact, address):
        self.set_font("Arial", "B", self.font_size + 6)
        self.cell(0, 10, name, ln=True)

        self.set_font("Arial", "", self.font_size)
        self.multi_cell(0, 8, contact)
        self.cell(0, 8, address, ln=True)
        self.ln(5)

    def add_section_title(self, title):
        self.set_font("Arial", "B", self.font_size + 2)
        self.cell(0, 10, title.upper(), ln=True)
        self.add_separator()

    def add_summary(self, summary):
        self.set_font("Arial", "", self.font_size)
        self.multi_cell(0, 8, summary)
        self.ln(4)

    def add_skills(self, skills):
        self.set_font("Arial", "", self.font_size)
        col_width = 60
        row_height = 8
        for index in range(0, len(skills), 3):
            for i in range(3):
                if index + i < len(skills):
                    self.cell(col_width, row_height, skills[index + i], border=0)
            self.ln(row_height)
        self.ln(4)

    def add_projects(self, projects):
        for project in projects:
            self.set_font("Arial", "B", self.font_size)
            self.cell(0, 8, project.get('title', 'Untitled'), ln=True)

            self.set_font("Arial", "", self.font_size)
            self.multi_cell(0, 8, project.get('description', ''))
            self.ln(3)

    def generate(self, resume):
        # Build contact details from individual fields
        contact_info = f"Phone: {resume.get('phone', '')}\nEmail: {resume.get('email', '')}\nTwitter: {resume.get('twitter', '')}"
        self.add_header(resume.get("name", "N/A"), contact_info, resume.get("address", ""))

        # Summary section
        if "summary" in resume:
            self.add_section_title(resume.get("headline", "Summary"))
            self.add_summary(resume["summary"])

        # Skills section
        if "skills" in resume and resume["skills"]:
            self.add_section_title("Skills")
            self.add_skills(resume["skills"])

        # Projects section
        if "projects" in resume and resume["projects"]:
            self.add_section_title("Projects")
            self.add_projects(resume["projects"])


def main():
    parser = argparse.ArgumentParser(description="Generate a resume PDF from API data.")
    parser.add_argument("--name", required=True, help="Candidate name for resume API.")
    parser.add_argument("--font-size", type=int, default=12, help="Text size.")
    parser.add_argument("--font-color", type=convert_color, default="#000000", help="Text color.")
    parser.add_argument("--background-color", type=convert_color, default="#FFFFFF", help="Page background color.")
    parser.add_argument("--output", default="resume.pdf", help="Filename for the output PDF.")
    args = parser.parse_args()

    print("📡 Collecting resume info...")
    resume_info = get_resume_data(args.name)

    resume_pdf = PDFResume(args.font_size, args.font_color, args.background_color)
    resume_pdf.generate(resume_info)
    resume_pdf.output(args.output)
    print(f"✅ Resume generated: {args.output}")


if __name__ == "__main__":
    main()
