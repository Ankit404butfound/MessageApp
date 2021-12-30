package main

import (
    "os"
    "log"
    "net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
    //fmt.Fprintf(w, "Hi there, I love %s!", r.FormValue("name"))
    w.Write([]byte(`{"status":"OK"}`))
}

func main() {
    port := os.Getenv("PORT")
    http.HandleFunc("/", handler)
    log.Fatal(http.ListenAndServe(":"+port, nil))
}
