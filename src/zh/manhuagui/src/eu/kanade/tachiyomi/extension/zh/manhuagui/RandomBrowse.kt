package eu.kanade.tachiyomi.extension.zh.manhuagui

import eu.kanade.tachiyomi.source.model.MangasPage
import eu.kanade.tachiyomi.source.model.SManga
import org.jsoup.nodes.Document
import org.jsoup.nodes.Element
import java.util.concurrent.ConcurrentHashMap
import kotlin.random.Random

/**
 * Shuffles the order of remote website pages for one filter set.
 *
 * A new page order is generated whenever Mihon loads its first page.
 * Each subsequent page keeps the same order until the next refresh.
 * Individual remote page numbers are not repeated within a session.
 */
internal class RandomBrowse {
    private data class Session(
        val pageOrder: List<Int>,
        val shuffleSeed: Long,
    )

    private val sessions = ConcurrentHashMap<String, Session>()

    suspend fun getPage(
        page: Int,
        key: String,
        fetch: suspend (Int) -> Document,
        parseManga: (Element) -> SManga,
    ): MangasPage {
        if (page < 1) return MangasPage(emptyList(), false)

        var firstPageDocument: Document? = null
        val existing = sessions[key]
        val session = if (page == 1 || existing == null) {
            val first = fetch(1)
            firstPageDocument = first

            // Avoid generating additional remote requests for empty filters.
            if (first.select("ul#contList > li").isEmpty()) {
                return MangasPage(emptyList(), false)
            }

            val totalPages = first.select("a[href]")
                .flatMap { link -> PAGE_REGEX.findAll(link.attr("href")).mapNotNull { it.groupValues[1].toIntOrNull() }.toList() }
                .maxOrNull() ?: 1

            Session(
                pageOrder = (1..totalPages).shuffled(),
                shuffleSeed = Random.nextLong(),
            ).also { sessions[key] = it }
        } else {
            existing
        }

        val remotePage = session.pageOrder.getOrNull(page - 1) ?: return MangasPage(emptyList(), false)
        val document = firstPageDocument?.takeIf { remotePage == 1 } ?: fetch(remotePage)

        val mangas = document.select("ul#contList > li")
            .map(parseManga)
            .shuffled(Random(session.shuffleSeed xor remotePage.toLong()))

        return MangasPage(mangas, page < session.pageOrder.size)
    }

    private companion object {
        val PAGE_REGEX = Regex("""view_p(\d+)\.html""")
    }
}
