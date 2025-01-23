(async _ => {
    res = [];
    for (continent of 'AS AF NA SA AN EU'.split(' ')) res = [...res, ...await (await fetch(`https://hitchwiki.org/maps/api/?continent=${continent}`)).json()];
    out = [];
    for (r of res) {
        txt = '<';
        while (txt.startsWith('<'))
            try {
                await new Promise(r => setTimeout(r, 1000));
                txt = await (await fetch(`https://hitchwiki.org/maps/api/?lang=en_UK&place=${r.id}`)).text();
            } catch (e) {}
        out.push(txt)
        if (Math.random() < 0.001) console.log(out)
    }
    console.log('done');
})()
