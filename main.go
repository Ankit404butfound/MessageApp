package main

import (
	"crypto/rand"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	_ "github.com/lib/pq"
)

var db, _ = sql.Open("postgres", os.Getenv("DATABASE_URL"))

type User struct {
	USERNAME  string `json:"username"`
	FIRSTNAME string `json:"first_name"`
	LASTNAME  string `json:"last_name"`
}

type Message struct {
	MSG_ID        int    `json:"msg_id"`
	FROM_USERNAME string `json:"from_username"`
	TO_USERNAME   string `json:"to_username"`
	MESSAGE       string `json:"message"`
}

func randomHex() string {
	bytes := make([]byte, 10)
	if _, err := rand.Read(bytes); err != nil {
		return ""
	}
	return hex.EncodeToString(bytes)
}

func createTable(w http.ResponseWriter, r *http.Request) {
	//_, err := db.Exec("DROP TABLE messages")
	ins, err := db.Query("CREATE TABLE messages (msg_id SERIAL, from_username varchar(20), to_username varchar(20), message varchar(65000), status varchar(4))")
	ins.Close()
	//_, err := db.Exec("CREATE TABLE users (username varchar(20) PRIMARY KEY, password varchar(20), first_name varchar(255), last_name varchar(255))")
	if err != nil {
		fmt.Fprint(w, err)
	} else {
		fmt.Fprint(w, "{\"status\":200, \"msg\": \"Success\"}")
	}

}

func createUser(w http.ResponseWriter, r *http.Request) {
	var userid int
	f_name := r.FormValue("first_name")
	l_name := r.FormValue("last_name")
	username := r.FormValue("username")
	password := randomHex()
	fmt.Printf("%s %s %s %d\n", f_name, l_name, password, userid)

	ins, err := db.Query("INSERT INTO users (username, password, first_name, last_name) VALUES ($1, $2, $3, $4)", username, password, f_name, l_name)
	ins.Close()
	if err != nil {
		fmt.Fprint(w, "{status: 404, \"msg\": \""+err.Error()+"\"}")
	} else {
		fmt.Fprint(w, "{\"status\":200, \"msg\": \"Success\", \"user_info\": {\"username\":\""+username+"\", \"password\": \""+password+"\", \"first_name\": \""+f_name+"\", \"last_name\": \""+l_name+"\"}}")
	}
}

func check_new_messages(w http.ResponseWriter, r *http.Request) {
	var lst []Message
	var db_password string
	username := string(r.FormValue("username"))
	password := string(r.FormValue("password"))

	row, _ := db.Query("SELECT password FROM users WHERE username ='" + username + "'")
	for row.Next() {
		row.Scan(&db_password)
	}
	row.Close()

	if password != db_password {
		fmt.Fprint(w, "{status: 404, \"msg\": \"INVALID USERNAME OR PASSWORD\"}")
		return
	}

	row, _ = db.Query("SELECT msg_id, from_username, to_username, message FROM messages WHERE to_username = $1 and status = 'new'", username)

	for row.Next() {
		var temp Message
		_ = row.Scan(&temp.MSG_ID, &temp.FROM_USERNAME, &temp.TO_USERNAME, &temp.MESSAGE)
		lst = append(lst, temp)
		temp_row, _ := db.Query("UPDATE messages set status = 'old' WHERE to_username = $1 and msg_id = $2", username, temp.MSG_ID)
		temp_row.Close()
	}
	row.Close()
	jsn, _ := json.Marshal(lst)
	if len(lst) > 0 {
		fmt.Fprint(w, "{\"data\":"+string(jsn)+",\"status\":200, \"msg\": \"Success\"}")
	} else {
		fmt.Fprint(w, "{\"status\": 200, \"data\": [], \"msg\": \"Success\"}")
	}
}

func check_all_messages(w http.ResponseWriter, r *http.Request) {
	var lst []Message
	var db_password string
	username := string(r.FormValue("username"))
	password := string(r.FormValue("password"))

	row, _ := db.Query("SELECT password FROM users WHERE username ='" + username + "'")
	for row.Next() {
		row.Scan(&db_password)
	}
	row.Close()
	fmt.Println(username)
	if password != db_password {
		fmt.Fprint(w, "{\"status\": 404, \"msg\": \"INVALID USERNAME OR PASSWORD\"}")
		return
	}

	row, _ = db.Query("SELECT msg_id, from_username, to_username, message FROM messages WHERE to_username = $1 or from_username = $1", username)

	for row.Next() {
		var temp Message
		_ = row.Scan(&temp.MSG_ID, &temp.FROM_USERNAME, &temp.TO_USERNAME, &temp.MESSAGE)
		lst = append(lst, temp)
	}
	row.Close()
	jsn, _ := json.Marshal(lst)
	if len(lst) > 0 {
		fmt.Fprint(w, "{\"data\":"+string(jsn)+",\"status\":200, \"msg\": \"Success\"}")
	} else {
		fmt.Fprint(w, "{\"status\": 200, \"data\": [], \"msg\": \"Success\"}")
	}
}

func check_messages_for_particular_user(w http.ResponseWriter, r *http.Request) {
	var lst []Message
	var db_password string
	username := string(r.FormValue("username"))
	password := string(r.FormValue("password"))
	from_user := string(r.FormValue("from_user"))

	row, _ := db.Query("SELECT password FROM users WHERE username ='" + username + "'")
	for row.Next() {
		row.Scan(&db_password)
	}
	row.Close()
	fmt.Println(username)
	if password != db_password {
		fmt.Fprint(w, "{\"status\": 404, \"msg\": \"INVALID USERNAME OR PASSWORD\"}")
		return
	}

	row, _ = db.Query("SELECT msg_id, from_username, to_username, message FROM messages where from_username in ($1, $2) and to_username in ($1, $2) ORDER BY msg_id", username, from_user)

	for row.Next() {
		var temp Message
		_ = row.Scan(&temp.MSG_ID, &temp.FROM_USERNAME, &temp.TO_USERNAME, &temp.MESSAGE)
		lst = append(lst, temp)
	}
	row.Close()
	jsn, _ := json.Marshal(lst)
	if len(lst) > 0 {
		fmt.Fprint(w, "{\"data\":"+string(jsn)+",\"status\":200, \"msg\": \"Success\"}")
	} else {
		fmt.Fprint(w, "{\"status\": 200, \"data\": [], \"msg\": \"Success\"}")
	}
}

func get_user(w http.ResponseWriter, r *http.Request) {
	var user User
	var db_password string
	by_username := string(r.FormValue("by_username"))
	username := string(r.FormValue("username"))
	password := string(r.FormValue("password"))

	row, _ := db.Query("SELECT password FROM users WHERE username ='" + by_username + "'")
	for row.Next() {
		row.Scan(&db_password)
	}
	row.Close()

	if password != db_password {
		fmt.Fprint(w, "{\"status\": 404, \"msg\": \"INVALID USERNAME OR PASSWORD\"}")
		return
	}

	row, _ = db.Query("SELECT first_name, last_name, username FROM users WHERE username = $1", username)

	for row.Next() {
		_ = row.Scan(&user.FIRSTNAME, &user.LASTNAME, &user.USERNAME)
	}
	row.Close()
	jsn, _ := json.Marshal(user)
	fmt.Fprint(w, "{\"data\":"+string(jsn)+",\"status\":200, \"msg\": \"Success\"}")
}

func send_message(w http.ResponseWriter, r *http.Request) {
	var db_password string
	var db_username string
	from_username := string(r.FormValue("from_username"))
	to_username := string(r.FormValue("to_username"))
	password := string(r.FormValue("password"))
	message := string(r.FormValue("message"))
	status := "new"

	row, _ := db.Query("SELECT password FROM users WHERE username ='" + from_username + "'")
	for row.Next() {
		_ = row.Scan(&db_password)
	}
	fmt.Println(db_password)
	row.Close()
	if db_password != password {
		fmt.Fprint(w, "{\"status\":404, \"msg\": \"Wrong password\"}")
		return
	} else {
		row, _ = db.Query("SELECT username FROM users WHERE username ='" + to_username + "'")
		for row.Next() {
			_ = row.Scan(&db_username)
		}
		row.Close()
		fmt.Println(db_username)
		if db_username == "" {
			fmt.Fprint(w, "{\"status\":404, \"msg\": \"User not found\"}")
			return
		} else {
			row, err := db.Query("INSERT INTO messages (from_username, to_username, message, status) VALUES ($1, $2, $3, $4)", from_username, to_username, message, status)
			row.Close()
			if err != nil {
				fmt.Fprint(w, "{status: 404, \"msg\": \""+err.Error()+"\"}")
			} else {
				fmt.Fprint(w, "{\"status\":200, \"msg\": \"Success\"}")
			}
		}
	}

	//db.Close()
}

func main() {
	//var user User

	http.HandleFunc("/check_new_messages", check_new_messages)
	http.HandleFunc("/check_all_messages", check_all_messages)
	http.HandleFunc("/check_messages_for_particular_user", check_messages_for_particular_user)
	http.HandleFunc("/send_message", send_message)
	http.HandleFunc("/get_user", get_user)
	http.HandleFunc("/create", createTable)
	http.HandleFunc("/register", createUser)
	fmt.Println("SERVER STARTED!")
	http.ListenAndServe(":"+os.Getenv("PORT"), nil)

	// fmt.Println(string(b))

}
