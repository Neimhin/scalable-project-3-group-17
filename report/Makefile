
example_interest_packet.json.pdf: example_interest_packet.json
	enscript --color -E -B -fCourier10 -o - $< | ps2pdf - $@
	pdfcrop $@ $@
