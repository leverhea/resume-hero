import fitz

doc = fitz.open("/var/home/leverhea/Downloads/Lucas_Everheart.pdf")
text = ""
for page in doc:
    text += page.get_text()
doc.close()

print(text)
