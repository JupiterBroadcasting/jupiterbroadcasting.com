/* Query URLs */
const JoopTubeURL = new URL("https://jupiter.tube/api/v1/");
const JoopTubeQuery =
    ({ isLive }) => new URL("video-channels/live/videos?" +
        `isLive=${isLive ? true : false}` + // Normally redundant, avoids injection
        `&skipCount=false` +
        `&count=1` +
        `&sort=-createdAt`,
        JoopTubeURL);

/**
 * Gets the embedable link from a PeerTube Video object passed via Promise
 * 
 * This assumes the result of the promise of is an API repsonse
 *      with at least one result. If no shows are live the API response
 *      will be undefined at `promiseResult.value`, don't poke it.
 * 
 * @param {PromiseSettledResult<Response>} show The final result of either fetch call above
 * @returns {URL | undefined} The URL object referencing the embedable video
 */
const getEmbedLink = show => {
    if (!show || show.status === 'rejected') {
        return undefined
    }

    const promiseResult = show.value
    /**
     * @const 
     * @type {string | undefined}
     */
    const embedPath = promiseResult.data?.[0]?.embedPath;
    return !embedPath ? undefined : new URL(embedPath, JoopTubeURL);
};

/**
 * Queries the 'live' channel at jupiter.tube for either
 *      a) the embed link of the currently live show
 *      OR
 *      b) the embed link of the most recently aired show
 * @returns {string} The embedable URL
 */
async function jbLive() {
    const headers = new Headers({
        "Accept": "application/json"
    });

    const requestOptions = {
        method: 'GET',
        headers: headers,
        redirect: 'follow'
    };

    const liveShowQuery = fetch(JoopTubeQuery({ isLive: true }), requestOptions)
        .then(response => response.text())
        .then(result => JSON.parse(result))
        .catch(error => console.error('Error while fetching live URL!', error));

    const archivedShowQuery = fetch(JoopTubeQuery({ isLive: false }), requestOptions)
        .then(response => response.text())
        .then(result => JSON.parse(result))
        .catch(error => console.error(('Error while fetching live URL!', error)));

    const [liveShow, archivedShow] = await Promise.allSettled([liveShowQuery, archivedShowQuery])

    return getEmbedLink(liveShow)?.toString() ?? getEmbedLink(archivedShow)?.toString();
}