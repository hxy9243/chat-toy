<template>
    <v-container>
        <v-row>
            <v-col cols=4>
                <v-card>
                    <v-card-item>
                        <v-row>
                            <v-select v-model=selectedDocument label="Documents" :items=this.documents item-title="name"
                                item-value="id" @update:modelValue="handleSelectDocument"></v-select>
                        </v-row>
                    </v-card-item>
                    <v-card-actions>
                        <v-row>
                            <v-col>
                                <v-btn color="red">Delete</v-btn>
                            </v-col>
                            <v-col>
                                <DocumentAdd :url=this.url v-model="dialog" @addDocument="handleAddDocument" />
                            </v-col>
                        </v-row>
                    </v-card-actions>
                </v-card>
            </v-col>
            <v-col cols=8>
                <div>
                    <v-textarea v-model="documentBody" readonly>
                    </v-textarea>
                </div>
            </v-col>

        </v-row>
    </v-container>
</template>

<script>

import DocumentAdd from './DocumentAdd.vue';

export default {
    props: ['url'],
    components: {
        DocumentAdd,
    },
    data() {
        return {
            documents: [],
            documentMap: {},
            documentBody: '',
            selectedDocument: null,
            dialog: null,
        };
    },
    mounted() {
        this.fetchDocuments();
    },
    methods: {
        fetchDocuments() {
            // Make an API request to fetch the documents from your backend
            // Replace the URL with your actual API endpoint
            fetch(this.url + '/api/documents')
                .then((response) => response.json())
                .then((data) => {
                    this.documents = data;
                    this.documentMap = data.reduce((map, object) => {
                        map[object.id] = object;
                        return map;
                    }, {});
                })
                .catch((error) => {
                    console.error('Error fetching documents:', error);
                });
        },
        handleSelectDocument(value) {
            console.log(this.documentMap[value].body);

            this.documentBody = this.documentMap[value].body;
        },
        handleAddDocument(document) {
            this.documents.push(document);

            this.documentMap[document.id] = document;
        },
        handleClick() {
            console.log("FUCKLASJDKAJSDFK");
        },
    },
};
</script>

