<template>
    <v-row>
        <v-col cols="4" md="4">
            <v-dialog v-model="dialog">
                <template v-slot:activator="{ props }">
                    <v-btn color="green" v-bind="props">
                        Create
                    </v-btn>
                </template>

                <v-card>
                    <v-card-title>
                        <v-row>
                            <div>
                                <h2>
                                    Create a new Document
                                </h2>
                            </div>
                        </v-row>
                    </v-card-title>
                    <v-card-item>

                    </v-card-item>
                    <v-card-text>
                        <v-row>
                            <v-col cols="4">
                                <v-card>
                                    <v-row>
                                        <v-text-field label="Document Name" v-model="documentName"></v-text-field>
                                    </v-row>
                                    <v-row>
                                        <v-text-field label="URL" v-model="documentUrl" placeholder="https://">
                                        </v-text-field>
                                    </v-row>
                                </v-card>
                            </v-col>
                            <v-col cols="8">
                                <v-card>
                                    <v-row>
                                        <v-textarea label="Document" variant="outlined" v-model="documentBody"> Docuemnt
                                        </v-textarea>
                                    </v-row>
                                </v-card>
                            </v-col>
                        </v-row>
                    </v-card-text>
                    <v-card-actions>
                        <v-row>
                            <v-col>
                                <v-btn color="red" block @click="dialog = false">Close
                                    Dialog</v-btn>
                            </v-col>
                            <v-col>
                                <v-btn color="green" block @click="addDocument">Add</v-btn>
                            </v-col>
                        </v-row>
                    </v-card-actions>
                </v-card>
            </v-dialog>
        </v-col>
    </v-row>
</template>

<script>
export default {
    props: ['url', 'showDialog'],
    name: 'AddDocument',
    data() {
        return {
            documents: [],
            documentMap: {},
            documentName: '',
            documentUrl: '',
            documentBody: '',
            selectedDocument: null,
            dialog: null,
        };
    },
    methods: {
        addDocument() {
            this.$emit('addDocument', {
                'id': '1234',
                'name': 'yeah',
                'body': 'WOWWOWO',
            })
            this.dialog = false;
        },
    },
};
</script>
