from flask import Flask, render_template, request
from scraper import scrape_business_info

app = Flask(__name__)

@app.route("/business")
def business():
    doc_id = request.args.get("docId")
    if not doc_id:
        return "Missing Document ID", 400

    data = scrape_business_info(doc_id)
    return render_template("business.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
