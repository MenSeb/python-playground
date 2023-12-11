class WebSpider {
    constructor() {
        this.form = document.getElementById('form-spider');
        this.form.addEventListener('submit', this.submit)

        this.crawlButton = document.getElementById('crawl-button')
        this.crawlButton.addEventListener('click', this.crawlWebsite)
    }

    crawlWebsite = async (website) => {        
        const response = await fetch('/api/spider', {
            method: "POST",
            body: website
        })

        const json = await response.json()

        return json
    }

    submit = async (event) => {
        event.preventDefault()

        const formData = new FormData(this.form);

        const json = this.crawlWebsite(formData.get('url'))
        
        console.log({json});
    }
}

new WebSpider()