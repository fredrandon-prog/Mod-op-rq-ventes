package fr.mescourses.app

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

class GroceryDbHelper(context: Context) : SQLiteOpenHelper(context, "mescourses.db", null, 1) {

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            "CREATE TABLE items (" +
                "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                "name TEXT NOT NULL, " +
                "quantity INTEGER DEFAULT 1, " +
                "done INTEGER DEFAULT 0, " +
                "created_at INTEGER DEFAULT (strftime('%s','now')))"
        )
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS items")
        onCreate(db)
    }

    fun getAll(): List<GroceryItem> {
        val list = mutableListOf<GroceryItem>()
        readableDatabase.query("items", null, null, null, null, null, "done ASC, id DESC").use { c ->
            while (c.moveToNext()) {
                list.add(
                    GroceryItem(
                        id = c.getLong(c.getColumnIndexOrThrow("id")),
                        name = c.getString(c.getColumnIndexOrThrow("name")),
                        quantity = c.getInt(c.getColumnIndexOrThrow("quantity")),
                        done = c.getInt(c.getColumnIndexOrThrow("done")) == 1
                    )
                )
            }
        }
        return list
    }

    fun insert(name: String, quantity: Int = 1) {
        writableDatabase.execSQL("INSERT INTO items (name, quantity, done) VALUES (?, ?, 0)", arrayOf(name, quantity))
    }

    fun setDone(id: Long, done: Boolean) {
        writableDatabase.execSQL("UPDATE items SET done = ? WHERE id = ?", arrayOf(if (done) 1 else 0, id))
    }

    fun delete(id: Long) {
        writableDatabase.execSQL("DELETE FROM items WHERE id = ?", arrayOf(id))
    }

    fun clearDone() {
        writableDatabase.execSQL("DELETE FROM items WHERE done = 1")
    }
}
