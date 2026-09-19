package fr.mescourses.app

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

data class GroceryItem(val id: Long, val name: String, val quantity: Int, val done: Boolean)

class MainActivity : AppCompatActivity() {

    private lateinit var db: GroceryDbHelper
    private lateinit var adapter: ItemAdapter
    private val items = mutableListOf<GroceryItem>()

    private val scanLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) openScanner() else Toast.makeText(this, "Permission caméra refusée", Toast.LENGTH_SHORT).show()
        }

    private val scannerLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            val barcode = result.data?.getStringExtra("barcode")
            if (!barcode.isNullOrBlank()) {
                Toast.makeText(this, "Code: $barcode — recherche du produit…", Toast.LENGTH_SHORT).show()
                lookupAndAdd(barcode)
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        db = GroceryDbHelper(this)
        setContentView(R.layout.activity_main)

        val input = findViewById<EditText>(R.id.inputItem)
        val btnAdd = findViewById<Button>(R.id.btnAdd)
        val btnScan = findViewById<Button>(R.id.btnScan)
        val btnCarrefour = findViewById<Button>(R.id.btnCarrefour)
        val btnClear = findViewById<Button>(R.id.btnClearDone)
        val recycler = findViewById<RecyclerView>(R.id.recyclerItems)

        adapter = ItemAdapter(items,
            onToggle = { item -> toggleItem(item) },
            onDelete = { item -> deleteItem(item) },
            onOpenInCarrefour = { item -> openInCarrefour(item.name) })

        recycler.layoutManager = LinearLayoutManager(this)
        recycler.adapter = adapter

        btnAdd.setOnClickListener {
            val name = input.text.toString().trim()
            if (name.isNotEmpty()) {
                addItem(name)
                input.text.clear()
            }
        }

        btnScan.setOnClickListener {
            when {
                ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED -> openScanner()
                shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> scanLauncher.launch(Manifest.permission.CAMERA)
                else -> scanLauncher.launch(Manifest.permission.CAMERA)
            }
        }

        btnCarrefour.setOnClickListener { openInCarrefour(null) }

        btnClear.setOnClickListener { clearDone() }

        loadItems()
    }

    private fun loadItems() {
        items.clear()
        items.addAll(db.getAll())
        adapter.notifyDataSetChanged()
    }

    private fun addItem(name: String) {
        db.insert(name)
        loadItems()
    }

    private fun toggleItem(item: GroceryItem) {
        db.setDone(item.id, !item.done)
        loadItems()
    }

    private fun deleteItem(item: GroceryItem) {
        db.delete(item.id)
        loadItems()
    }

    private fun clearDone() {
        db.clearDone()
        loadItems()
    }

    private fun openScanner() {
        scannerLauncher.launch(Intent(this, ScannerActivity::class.java))
    }

    private fun lookupAndAdd(barcode: String) {
        CoroutineScope(Dispatchers.Main).launch {
            val name = withContext(Dispatchers.IO) { fetchProductName(barcode) }
            if (name != null) {
                addItem(name)
                Toast.makeText(this@MainActivity, "Ajouté : $name", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this@MainActivity, "Produit inconnu (code $barcode)", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun fetchProductName(barcode: String): String? {
        return try {
            val url = URL("https://world.openfoodfacts.org/api/v2/product/$barcode.json?fields=product_name,brands")
            val conn = url.openConnection() as HttpURLConnection
            conn.connectTimeout = 10000
            conn.readTimeout = 10000
            conn.setRequestProperty("User-Agent", "MesCourses/1.0 (android)")
            val body = conn.inputStream.use { it.readBytes().toString(Charsets.UTF_8) }
            val json = JSONObject(body)
            if (json.optInt("status") != 1) return null
            val product = json.getJSONObject("product")
            val name = product.optString("product_name").trim()
            val brand = product.optString("brands").split(",")?.firstOrNull()?.trim()
            when {
                name.isNotEmpty() && !brand.isNullOrEmpty() -> "$name ($brand)"
                name.isNotEmpty() -> name
                else -> null
            }
        } catch (e: Exception) {
            null
        }
    }

    private fun openInCarrefour(query: String?) {
        val search = query?.takeIf { it.isNotBlank() } ?: items.filter { !it.done }.joinToString(" ") { it.name }
        val url = if (search.isBlank())
            "https://www.carrefour.fr/"
        else
            "https://www.carrefour.fr/recherche?q=" + URLEncoder.encode(search, "UTF-8")
        try {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
        } catch (e: Exception) {
            Toast.makeText(this, "Aucune application pour ouvrir ce lien", Toast.LENGTH_SHORT).show()
        }
    }

    inner class ItemAdapter(
        private val data: List<GroceryItem>,
        private val onToggle: (GroceryItem) -> Unit,
        private val onDelete: (GroceryItem) -> Unit,
        private val onOpenInCarrefour: (GroceryItem) -> Unit
    ) : RecyclerView.Adapter<ItemAdapter.VH>() {

        inner class VH(view: View) : RecyclerView.ViewHolder(view) {
            val text: TextView = view.findViewById(R.id.itemName)
            val btnDelete: Button = view.findViewById(R.id.btnDelete)
            val btnCarrefour: Button = view.findViewById(R.id.btnItemCarrefour)
            val root: LinearLayout = view as LinearLayout
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val v = LayoutInflater.from(parent.context).inflate(R.layout.item_grocery, parent, false)
            return VH(v)
        }

        override fun getItemCount(): Int = data.size

        override fun onBindViewHolder(holder: VH, position: Int) {
            val item = data[position]
            holder.text.text = if (item.quantity > 1) "${item.name} ×${item.quantity}" else item.name
            holder.root.alpha = if (item.done) 0.5f else 1f
            holder.text.setOnClickListener { onToggle(item) }
            holder.btnDelete.setOnClickListener { onDelete(item) }
            holder.btnCarrefour.setOnClickListener { onOpenInCarrefour(item) }
        }
    }
}
