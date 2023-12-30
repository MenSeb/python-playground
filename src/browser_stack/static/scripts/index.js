class BrowserStack {
    constructor() {
        this.form = document.querySelector('form');
        this.form.addEventListener('change', this.dispatchChange);
        this.form.addEventListener('submit', this.start);
        this.form.addEventListener('reset', this.stop);

        this.selectBrowser = this.form.elements['select-browser'];
        this.selectDevice = this.form.elements['select-device'];

        this.inputHeight = this.form.elements['input-height'];
        this.inputWidth = this.form.elements['input-width'];

        // this.inputHost = this.form.elements['input-host'];
        // this.inputPort = this.form.elements['input-host'];

        this.breakpointsNodeList = this.form.elements['breakpoint'];
    }

    dispatchChange = (event) => {
        const { target } = event;

        switch (target) {
            case this.selectDevice:
                return this.onSelectDevice(event);
            case this.selectBrowser:
                return this.onSelectBrowser(event);
            default:
                if (target.getAttribute('name') === 'breakpoint')
                    return this.onSelectBreakpoint(event);

                console.log('UNHANDLE EVENT', event);
        }
    };

    enableSizeInput = (input) => {
        input.removeAttribute('disabled');
        input.setAttribute('aria-disabled', 'false');
        input.setAttribute('required', true);
    };

    disableSizeInput = (input) => {
        input.removeAttribute('required');
        input.setAttribute('disabled', true);
        input.setAttribute('aria-disabled', 'true');
    };

    updateInputHeight = (value) => {
        this.inputHeight.value = value;
    };

    updateInputWidth = (value) => {
        this.inputWidth.value = value;
    };

    onSelectBrowser = (event) => {
        console.log('SELECT BROWSER', event);
    };

    onSelectDevice = (event) => {
        console.log('SELECT DEVICE', event);

        const { selectedOptions } = this.selectDevice;
        const selectedOption = selectedOptions[0];
        const { height, width } = selectedOption.dataset;

        this.updateInputHeight(height);
        this.updateInputWidth(width);

        if (selectedOption.value === 'custom') {
            this.enableSizeInput(this.inputHeight);
            this.enableSizeInput(this.inputWidth);
        } else if (this.inputHeight.hasAttribute('required')) {
            console.log('DISABLE');
            this.disableSizeInput(this.inputHeight);
            this.disableSizeInput(this.inputWidth);
        }

        if (selectedOption.value !== '') {
            const { value: valueBreakpoint } = this.breakpointsNodeList;

            if (valueBreakpoint !== '') {
                const checkedBreakpoint = this.form.querySelector(
                    `[name=breakpoint][value="${valueBreakpoint}"]`,
                );

                checkedBreakpoint.checked = false;
            }
        }
    };

    onSelectBreakpoint = (event) => {
        console.log('SELECT BREAKPOINT', event);

        const { value: selectedDevice } = this.selectDevice;

        if (selectedDevice !== '') {
            console.log('RESET DEIVCE');

            this.selectDevice.value = '';

            this.updateInputHeight('');
            this.updateInputWidth('');

            if (this.inputHeight.hasAttribute('required')) {
                console.log('DISABLE');
                this.disableSizeInput(this.inputHeight);
                this.disableSizeInput(this.inputWidth);
            }
        }
    };

    start = async (event) => {
        event.preventDefault();

        const formData = new FormData(this.form);

        if (this.selectDevice.value !== 'custom') {
            formData.append(this.inputHeight.name, this.inputHeight.value);
            formData.append(this.inputWidth.name, this.inputWidth.value);
        }

        const response = await fetch('/api/browser/start', {
            body: formData,
            method: 'POST',
        });

        const json = await response.json();

        console.log(json);
    };

    stop = async (event) => {
        event.preventDefault();

        const response = await fetch('/api/browser/stop');

        const json = await response.json();

        console.log(json);
    };
}

new BrowserStack();
