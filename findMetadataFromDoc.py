# import parser object from tike
from tika import parser

# opening pdf file
parsed_pdf = parser.from_file("/home/bisag/Documents/impNotes/1postgis_turf_gis.pdf")

# saving content of pdf
# you can also bring text only, by parsed_pdf['text']
# parsed_pdf['content'] returns string
data = parsed_pdf['content']

# Printing of content
#print(data)

print(parsed_pdf['metadata']) 
  
# <class 'dict'>
print(type(parsed_pdf['metadata']))