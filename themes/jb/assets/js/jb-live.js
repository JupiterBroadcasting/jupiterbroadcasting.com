const JoopTubeURL = new URL("https://jupiter.tube/api/v1/")
// This query shouldn't be merged to main, it's very dirty. Almost naughty, not ready for the big leagues
const JoopTubeQuery = 
({isLive}) => new URL("video-channels/live/videos?" +
        `isLive=${isLive ? true : false}` + // Normally redundant, avoids injection
        `&skipCount=false` +
        `&count=1` +
        `&sort=-createdAt`,
    JoopTubeURL)

async function jbLive() {
    const headers = new Headers({
        "Accept": "application/json"
    });

    const requestOptions = {
        method: 'GET',
        headers: headers,
        redirect: 'follow'
    };

    const liveShowQuery = fetch(JoopTubeQuery({isLive: true}), requestOptions)
        .then(response => response.text())
        .then(result => JSON.parse(result))
        //.then(result => result.value)
        .catch(error => console.error('Error while fetching live URL!', error));
    
    const archivedShowQuery = fetch(JoopTubeQuery({isLive: false}), requestOptions)
        .then(response => response.text())
        .then(result => JSON.parse(result))
        .catch(error => console.error(('Error while fetching live URL!', error)))

    const getEmbedLink = show => {
        const embedPath = show?.value?.data?.[0]?.embedPath
        return !embedPath ? undefined : new URL(embedPath, JoopTubeURL);
    }

    const [liveShow, archivedShow] = await Promise.allSettled([liveShowQuery, archivedShowQuery])

    return getEmbedLink(liveShow).toString() ?? getEmbedLink(archivedShow).toString()
}