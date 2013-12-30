from re import escape

def fdf_escape(text):
	if not text:
		return ''
	else:
		return escape(text)


def create_fdf(filename, formname, fields):
    fdf = open(filename, 'w')

    fdf.write("%FDF-1.2\n")
    fdf.write("%????\n")
    fdf.write("1 0 obj<</FDF<</F(" + formname + ")/Fields 2 0 R>>>>\n")
    fdf.write("endobj\n")
    fdf.write("2 0 obj[\n\n")

    for field in fields:
        fdf.write("<</T(topmostSubform[0].Page1[0].%s[0])/V(%s)>>\n" % (field, fdf_escape(fields[field])))

    fdf.write("]\n")
    fdf.write("endobj\n")
    fdf.write("trailer\n")
    fdf.write("<</Root 1 0 R>>\n")
    fdf.write("%%EO\n")

    fdf.close()
