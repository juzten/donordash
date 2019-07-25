import Vue from "vue"
import App from "./App.vue"
import axios from "axios"
import "vuetify/dist/vuetify.min.css"
import vuetify from "./plugins/vuetify"

Vue.config.productionTip = false

const donations_api = axios.create({
    baseURL: "https://ad35088f.ngrok.io/api/"
})

Vue.donations_api = Vue.prototype.$donations_api = donations_api

new Vue({
    vuetify,
    render: h => h(App)
}).$mount("#app")
