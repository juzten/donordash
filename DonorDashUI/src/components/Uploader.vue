<template>
    <v-layout justify-center>
        <v-dialog v-model="uploadDialog" persistent max-width="600px">
            <v-card>
                <v-card-title>
                    <span class="headline">New Donations</span>
                </v-card-title>
                <v-subheader>Please upload new donations in a csv file format only.</v-subheader>
                <v-card-text>
                    <v-container grid-list-md>
                        <v-layout wrap>
                            <v-flex xs12>
                                <v-form ref="form" enctype="multipart/form-data">
                                    <v-flex>
                                        <v-text-field
                                            v-model="email"
                                            label="Email"
                                            hint="A notification will be sent to this email when the uploaded file has finished processing"
                                            persistent-hint
                                        />
                                    </v-flex>
                                    <v-file-input
                                        v-model="donation_file"
                                        accept=".csv"
                                        label="CSV File input"
                                        required
                                        :rules="[value => (value || {}).size > 0 || 'File is required!']"
                                    />
                                </v-form>
                            </v-flex>
                        </v-layout>
                    </v-container>
                </v-card-text>
                <v-card-actions>
                    <v-spacer />
                    <v-btn color="blue darken-1" text @click="$emit('close-dialog')">Close</v-btn>
                    <v-btn color="blue darken-1" text @click="submitFile()">Save</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-layout>
</template>

<script>
import axios from "axios"

export default {
    props: {
        uploadDialog: Boolean
    },
    data: () => ({
        donation_file: [],
        email: ""
    }),
    methods: {
        submitFile: function() {
            if (this.$refs.form.validate()) {
                if (this.donation_file.type === "text/csv") {
                    this.$emit("close-dialog")
                    const formData = new FormData()
                    if (this.email !== "") {
                        formData.append("email", this.email)
                    }
                    formData.append("donation_file", this.donation_file, this.donation_file.name)

                    this.$donations_api
                        .post("upload", formData)
                        .then(res => {
                            return this.$donations_api.post("process_donations")
                        })
                        .then(processRes => {
                            // Handle the response from the process_donations endpoint if needed
                            // console.log("Processing completed", processRes)
                        })
                        .catch(error => console.log(error))
                } else {
                    // show file type error
                }
            }
        }
    }
}
</script>
