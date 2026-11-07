package com.axiomzero.androidsuite

import android.content.Context
import org.json.JSONArray

data class Product(
    val id: String,
    val name: String,
    val version: String,
    val trl: String,
    val endpoint: String,
    val description: String,
    val folder: String
)

object PortfolioCatalog {
    fun load(context: Context): List<Product> {
        val json = context.assets.open("products.json").bufferedReader().use { it.readText() }
        val rows = JSONArray(json)
        val products = buildList(rows.length()) {
            for (index in 0 until rows.length()) {
                val row = rows.getJSONObject(index)
                add(
                    Product(
                        id = row.getString("id"),
                        name = row.getString("name"),
                        version = row.getString("version"),
                        trl = row.getString("trl"),
                        endpoint = row.getString("endpoint"),
                        description = row.getString("description"),
                        folder = row.getString("folder")
                    )
                )
            }
        }
        require(products.isNotEmpty()) { "The offline product catalog is empty." }
        require(products.map { it.id }.distinct().size == products.size) {
            "The offline product catalog contains duplicate IDs."
        }
        require(products.all { it.folder.startsWith("12-AZ-IP/") && ".." !in it.folder.split("/") }) {
            "The offline product catalog contains an unsafe folder."
        }
        return products
    }

    fun search(products: List<Product>, query: String): List<Product> {
        val terms = query.trim().lowercase().split(Regex("\\s+")).filter(String::isNotBlank)
        if (terms.isEmpty()) return products
        return products.filter { product ->
            val searchable = "${product.id} ${product.name} ${product.description} ${product.endpoint}"
                .lowercase()
            terms.all { term -> searchable.contains(term) }
        }
    }
}
