from re import escape

def fdf_value(text):
	if not text:
		# Convert None to empty string
		return ''
	else:
		returnText = []
		# Split text into lines; OS independent
		for line in text.splitlines():
			# Escape non-alphanumeric characters
			returnText.append(escape(line))
		# Return joined lines
		return '\n'.join(returnText)


def create_fdf(filename, formname, fields):
    fdf = open(filename, 'w')

    fdf.write("%FDF-1.2\n")
    fdf.write("%????\n")
    fdf.write("1 0 obj<</FDF<</F(" + formname + ")/Fields 2 0 R>>>>\n")
    fdf.write("endobj\n")
    fdf.write("2 0 obj[\n\n")

    for field in fields:
        fdf.write("<</T(topmostSubform[0].Page1[0].%s[0])/V(%s)>>\n" % (field, fdf_value(fields[field])))

    fdf.write("]\n")
    fdf.write("endobj\n")
    fdf.write("trailer\n")
    fdf.write("<</Root 1 0 R>>\n")
    fdf.write("%%EO\n")

    fdf.close()
