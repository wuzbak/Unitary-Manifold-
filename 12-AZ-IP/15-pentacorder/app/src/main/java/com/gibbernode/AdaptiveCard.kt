package com.gibbernode

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.gibbernode.gibberwave.AdaptiveStateHolder
import com.gibbernode.gibberwave.CardSeverity
import com.gibbernode.gibberwave.InjectedCard
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * AdaptiveCardSlot — renders assistant-injected cards for a given screen.
 *
 * Place this composable in any screen's Column to show live cards the
 * assistant has injected for that specific context.  Each card has a
 * dismiss button that removes it from [AdaptiveStateHolder].
 *
 * @param screenKey  The nav-route name of the host screen (e.g. "dashboard").
 *                   Pass null to show all injected cards regardless of screen.
 */
@Composable
fun AdaptiveCardSlot(
    assistantVm: AssistantViewModel,
    screenKey:   String? = null,
) {
    val adaptive by assistantVm.adaptiveState.collectAsState()

    val cards = if (screenKey == null) adaptive.dashboardCards
                else adaptive.dashboardCards  // all cards go to Dashboard for now

    val hint = screenKey?.let { adaptive.screenHints[it] }

    if (hint != null) {
        AssistantHintBanner(hint = hint, onDismiss = {
            assistantVm.executeAction(
                com.gibbernode.gibberwave.AssistantAction.ClearHint(screenKey)
            )
        })
    }

    cards.forEach { card ->
        InjectedCardView(card = card, onDismiss = {
            assistantVm.executeAction(
                com.gibbernode.gibberwave.AssistantAction.RemoveDashboardCard(card.id)
            )
        })
    }
}

@Composable
fun AssistantHintBanner(hint: String, onDismiss: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = GibberAmber.copy(alpha = 0.10f)),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.Top,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(
                text     = "💡 $hint",
                style    = MaterialTheme.typography.bodySmall,
                color    = GibberAmber,
                modifier = Modifier.weight(1f),
            )
            IconButton(onClick = onDismiss, modifier = Modifier.size(24.dp)) {
                Icon(Icons.Filled.Close, contentDescription = "Dismiss",
                    tint = OnSurfaceDim, modifier = Modifier.size(14.dp))
            }
        }
    }
}

@Composable
fun InjectedCardView(card: InjectedCard, onDismiss: () -> Unit) {
    val accentColor = when (card.severity) {
        CardSeverity.CRITICAL -> GibberRed
        CardSeverity.WARNING  -> GibberAmber
        CardSeverity.CAUTION  -> GibberAmber.copy(alpha = 0.7f)
        CardSeverity.INFO     -> GibberGreen
    }
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = accentColor.copy(alpha = 0.08f)),
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text       = "${card.icon} ${card.title}",
                    style      = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold,
                    color      = accentColor,
                )
                IconButton(onClick = onDismiss, modifier = Modifier.size(24.dp)) {
                    Icon(Icons.Filled.Close, contentDescription = "Dismiss",
                        tint = OnSurfaceDim, modifier = Modifier.size(14.dp))
                }
            }
            Text(
                text  = card.body,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface,
            )
        }
    }
}
