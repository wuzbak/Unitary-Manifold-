package com.axiomzero.androidsuite

import org.junit.Assert.assertEquals
import org.junit.Test

class PortfolioCatalogTest {
    private val products = listOf(
        Product("01", "Axiom OS Core Suite", "1.0", "TRL-5", "local", "Operating system", "12-AZ-IP/01-axiom-os/"),
        Product("14", "SDAM", "1.0", "TRL-3", "Android", "Mobile situational awareness", "12-AZ-IP/14-sdam/"),
        Product("46", "AxiomZero Android Suite", "0.1.0", "Not assessed", "Android", "Offline portfolio suite", "12-AZ-IP/46-axiomzero-android-suite/")
    )

    @Test
    fun searchMatchesAllTermsAcrossProductFields() {
        assertEquals(listOf("14"), PortfolioCatalog.search(products, "mobile android").map { it.id })
        assertEquals(listOf("46"), PortfolioCatalog.search(products, "46 suite").map { it.id })
        assertEquals(listOf("14"), PortfolioCatalog.search(products, "SDAM").map { it.id })
        assertEquals(listOf("14", "46"), PortfolioCatalog.search(products, "AnDrOiD").map { it.id })
    }

    @Test
    fun blankSearchKeepsCatalogOrder() {
        assertEquals(listOf("01", "14", "46"), PortfolioCatalog.search(products, "  ").map { it.id })
    }
}
