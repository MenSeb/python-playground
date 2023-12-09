class WebSpider {
    constructor() {
        this.form = document.getElementById('form-spider');
        this.form.addEventListener('submit', this.submit)
    }

    submit = async (event) => {
        event.preventDefault()

        const formData = new FormData(this.form);

        const response = await fetch('/api/spider', {
            method: "POST",
            body: formData
        })

        const json = await response.json()

        console.log({json});
    }
}

new WebSpider()