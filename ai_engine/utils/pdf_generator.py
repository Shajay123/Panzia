from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


def build_pdf(file_path, resume_text):

    doc = SimpleDocTemplate(
        file_path
    )

    styles = getSampleStyleSheet()

    content = []

    for line in resume_text.split("\n"):

        content.append(
            Paragraph(line, styles["BodyText"])
        )

        content.append(
            Spacer(1,5)
        )

    doc.build(content)




def generate_resume_pdf(data, response):

    styles = getSampleStyleSheet()

    story = []

    story.append(

        Paragraph(
            data["name"],
            styles["Title"]
        )
    )

    story.append(

        Paragraph(
            data["headline"],
            styles["Heading2"]
        )
    )

    story.append(

        Paragraph(
            data["bio"],
            styles["BodyText"]
        )
    )

    doc = SimpleDocTemplate(
        response
    )

    doc.build(story)