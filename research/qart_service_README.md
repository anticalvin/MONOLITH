# Local QArt service

Run from the repository root:

    python3 research/qart_service.py

POST JSON to http://127.0.0.1:8766/qart with url, version, and an image_base64
PNG/JPEG/WebP data URL stripped to base64. The service enforces an 8 MB source
limit and a 15 second process timeout. It passes fixed subprocess argument
arrays only; user data is never placed in a shell command.

Important: upstream QArt creates visual freedom by appending a URL fragment.
The raw decoded data therefore cannot satisfy byte-identical payload acceptance.
It is a navigation-equivalent experimental candidate, not a valid option when
the product requires exact decoded strings.
