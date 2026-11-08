const MAX_RESULTS = 20
const CANDIDATES = 60
const RECENCY_WEIGHT = 0.8
const RECENCY_HALF_LIFE_YEARS = 2
const TYPES = ['pick', 'sponsor', 'episode', 'show', 'person']
// Pagefind 1.5+ boosts title matches, so episodes titled "... Unplugged" outrank the show page itself.
const PROMOTED_TYPES = ['pick', 'sponsor', 'show', 'person']
const decoder = document.createElement('textarea')

let pagefind = null
let latest = 0

function decode(text) {
    decoder.innerHTML = text
    return decoder.value
}

function titleMatches(title, query) {
    const words = query.toLowerCase().split(/\s+/).filter(Boolean)
    const lower = (title || '').toLowerCase()
    return words.length > 0 && words.every(word => lower.includes(word))
}

function recency(dateText) {
    const age = (Date.now() - new Date(dateText).getTime()) / (365.25 * 24 * 3600 * 1000)
    if (!Number.isFinite(age)) return 0
    return Math.pow(0.5, Math.max(age, 0) / RECENCY_HALF_LIFE_YEARS)
}

function rankResults(results, query) {
    const top = Math.max(...results.map(r => r.score), 1)
    const adjusted = r => r.score / top + (r.meta.type === 'episode' ? RECENCY_WEIGHT * recency(r.meta.date) : 0)
    results = results.slice().sort((a, b) => adjusted(b) - adjusted(a))
    const promoted = PROMOTED_TYPES.flatMap(type => results.filter(r => r.meta.type === type && titleMatches(r.meta.title, query)))
    return promoted.concat(results.filter(r => !promoted.includes(r)))
}

function el(tag, className, text) {
    const node = document.createElement(tag)
    if (className) node.className = className
    if (text !== undefined) node.textContent = text
    return node
}

function renderExcerpt(excerpt) {
    const p = el('p', 'search-excerpt')
    excerpt.split(/(<mark>|<\/mark>)/).reduce((marked, part) => {
        if (part === '<mark>') return true
        if (part === '</mark>') return false
        if (part) {
            const text = decode(part)
            p.append(marked ? el('mark', '', text) : document.createTextNode(text))
        }
        return marked
    }, false)
    return p
}

function renderResult(result) {
    const type = TYPES.includes(result.meta.type) ? result.meta.type : 'episode'
    const external = Boolean(result.meta.link) && ['pick', 'sponsor'].includes(type)
    const href = external ? result.meta.link : result.url

    const card = el('div', 'search-result card')
    card.dataset.type = type
    const content = el('div', 'card-content')

    const tags = el('div', 'tags')
    tags.append(el('span', `tag search-type is-${type}`, type.toUpperCase()))
    if (type === 'episode' && result.meta.show) {
        tags.append(el('span', 'tag is-dark', result.meta.show))
    }
    if (type === 'pick' && result.meta.license) {
        tags.append(el('span', 'tag is-black', result.meta.license))
    }
    content.append(tags)

    const heading = el('h4')
    const link = el('a', '', result.meta.title || href)
    link.href = href
    if (external) {
        link.target = '_blank'
        link.rel = 'noopener'
        link.append(el('span', 'search-external', ' ↗'))
    }
    heading.append(link)
    content.append(heading)

    if (type === 'episode') {
        if (result.meta.date) content.append(el('div', 'search-muted', result.meta.date))
    }
    if (result.excerpt) content.append(renderExcerpt(result.excerpt))
    if (type === 'pick' && result.meta.episodes) {
        const addons = el('div', 'tags')
        addons.append(el('span', 'tag is-dark', result.meta.episodes))
        content.append(addons)
    }

    card.append(content)
    return card
}

function render(results, query) {
    const container = document.getElementById('search-results')
    const status = document.getElementById('search-status')
    container.replaceChildren()
    status.textContent = results.length ? '' : 'No results'
    container.append(...rankResults(results, query).slice(0, MAX_RESULTS).map(renderResult))
}

function clear() {
    document.getElementById('search-results').replaceChildren()
    document.getElementById('search-status').textContent = ''
}

async function runSearch(query) {
    const id = ++latest
    if (!query.trim()) {
        clear()
        return
    }
    const response = await pagefind.debouncedSearch(query)
    if (!response || id !== latest) return
    const results = await Promise.all(response.results.slice(0, CANDIDATES).map(async r => ({ ...(await r.data()), score: r.score })))
    if (id !== latest) return
    render(results, query)
}

async function init() {
    const input = document.getElementById('search-input')
    try {
        pagefind = await import('/pagefind/pagefind.js')
        await pagefind.init()
    } catch (error) {
        document.getElementById('search-status').textContent = 'Search is not available in this build'
        return
    }
    input.addEventListener('input', () => runSearch(input.value).catch(console.error))
    if (input.value.trim()) runSearch(input.value).catch(console.error)
}

window.addEventListener('DOMContentLoaded', init)
