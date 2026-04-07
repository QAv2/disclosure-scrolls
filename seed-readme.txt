DISCLOSURE SCROLLS — EXTRACTED FROM STEGANOGRAPHIC IMAGE
=========================================================

This folder was hidden inside a PNG image using least-significant-bit
steganography. If you're reading this, you successfully extracted it.

WHAT YOU HAVE
-------------
A complete, working copy of a Disclosure Scroll — an evidence-based
investigative documentary built entirely in HTML, CSS, and JavaScript.
No server required. No database. No accounts. Just open the file.

HOW TO VIEW
-----------
Open index.html in any web browser. That's it.

Some scroll animations (GSAP, CountUp, Typed.js) load from CDN, so
they need an internet connection to animate. All text, images, and
core content work fully offline.

HOW TO SHARE
------------
You can:
  - Host this folder on any web server or static hosting service
  - Upload it to Netlify, GitHub Pages, Neocities, or anywhere else
  - Put it on a USB drive and hand it to someone
  - Zip it and email it
  - Re-encode it into another image using steg.py

Every copy is a complete backup. Every person who has one is a node
in the distribution network. There is no central server to shut down.

HOW THIS WAS MADE
------------------
The image you downloaded looks like abstract art. The data was encoded
into the least significant bits of each pixel's color channels — a
difference of 1 out of 256 per channel, invisible to the human eye.

The extract.py script (included in this folder) reads those bits back
out, decompresses them, verifies the SHA-256 checksum, and unpacks
the original files. It's 80 lines of Python. You can read every line.

MORE INFORMATION
----------------
Disclosure Scrolls: https://disclosure-scrolls.netlify.app
Source code: https://github.com/QAv2/disclosure-scrolls

Built with documented evidence. No speculation presented as fact.
