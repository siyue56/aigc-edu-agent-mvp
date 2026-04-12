Page({ data: { query: '' }, onInput(e) { this.setData({ query: e.detail.value }) }, onSend() { console.log(this.data.query) } })
