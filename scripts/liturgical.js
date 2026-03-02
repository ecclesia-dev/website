/* liturgical.js — site accent from the 1962 Roman liturgical calendar */
(function () {
  var P = '#6B3FA0', W = '#C9A84C', R = '#C0392B';
  var G = '#2E7D32', K = '#1A1A1A', O = '#C2739A';

  /* Meeus/Jones/Butcher Easter algorithm */
  function easter(y) {
    var a = y % 19, b = Math.floor(y / 100), c = y % 100;
    var d = Math.floor(b / 4), e = b % 4;
    var f = Math.floor((b + 8) / 25);
    var g = Math.floor((b - f + 1) / 3);
    var h = (19 * a + b - d - g + 15) % 30;
    var i = Math.floor(c / 4), k = c % 4;
    var l = (32 + 2 * e + 2 * i - h - k) % 7;
    var m = Math.floor((a + 11 * h + 22 * l) / 451);
    var n = Math.floor((h + l - 7 * m + 114) / 31);
    var p = ((h + l - 7 * m + 114) % 31) + 1;
    return new Date(y, n - 1, p);
  }

  function days(a, b) { return Math.round((a - b) / 864e5); }

  function advent1(y) {
    var d = new Date(y, 10, 30).getDay();
    return new Date(y, 10, 30 - (d <= 3 ? d : d - 7));
  }

  function getLiturgicalColor(date) {
    var y = date.getFullYear(), m = date.getMonth(), d = date.getDate();
    var md = m * 100 + d, dow = date.getDay();
    var e = easter(y), de = days(date, e);

    /* Fixed feasts */
    if (md === 1002) return K;                          /* All Souls */
    if (md === 1001 || md === 1108) return W;           /* All Saints, Immac. Conception */
    if ((m === 11 && d >= 25) || (m === 0 && d <= 13)) return W; /* Christmas-Epiphany */
    if (md===102||md===225||md===524||md===715) return W;/* Purif, Annunc, Nat JB, Assumpt */
    if (md === 529 || md === 814) return R;              /* Sts Peter & Paul, Holy Cross */

    /* Moveable feasts (days from Easter) */
    if (de === -21) return O;                            /* Laetare Sunday */
    if (de === -3) return W;                             /* Maundy Thursday */
    if (de === -2) return K;                             /* Good Friday */
    if (de >= 0 && de <= 7) return W;                    /* Easter Octave */
    if (de === 39) return W;                             /* Ascension */
    if (de >= 49 && de <= 55) return R;                  /* Pentecost + Octave */
    if (de===56||de===60||de===68) return W;             /* Trinity, Corpus Christi, Sac. Heart */

    /* Advent */
    var adv = advent1(y);
    if (date >= adv && m === 11 && d <= 24) {
      if (days(date, adv) === 14 && dow === 0) return O;/* Gaudete Sunday */
      return P;
    }

    /* Lent: Ash Wednesday to Holy Saturday */
    if (de >= -46 && de <= -1) return P;

    /* Septuagesima: violet Sundays, green ferias */
    if (de >= -63 && de <= -47) return dow === 0 ? P : G;

    return G;                                            /* Ordinary Time */
  }

  document.documentElement.style.setProperty(
    '--liturgical-color', getLiturgicalColor(new Date())
  );
})();
