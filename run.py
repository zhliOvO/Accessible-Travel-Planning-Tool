import os
from insta485 import app


#----------------------------------------
# launch
#----------------------------------------

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 4000))
	app.run(host='0.0.0.0', port=port)
