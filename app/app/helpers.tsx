export const API_BASE = "http://localhost:8080/api/mock";
export const STATIC_BASE = "http://localhost:8080";

export function kgFormat(kg: number) {
    let value: string;
    let unit: string;
    if (kg < 1000) {
        value = Math.round(kg).toString();
        unit = "kg";
    } else if (kg < 1000000) {
        value = (kg / 1000).toFixed(2);
        unit = "t";
    } else {
        value = (kg / 1000000).toFixed(2);
        unit = "kt";
    }
    return value + " " + unit
}

export function secondsFormat(s: number) {
    // Return a string like "1h 2m"
    const hours = Math.floor(s / 3600);
    const minutes = Math.floor((s % 3600) / 60);
    let result = "";
    if (hours > 0) {
        result += hours + "h ";
    }
    if (minutes > 0) {
        result += minutes + "m";
    }
    return result;
}

export function dateFormat(unix: number) {
    const date = new Date(unix * 1000);
    return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
}

export function dollarFormat(d: number) {
    if (d > 999) {
        return "$" + (d / 1000).toFixed(1) + "k";
    }
    return "$" + d.toFixed(2);
}
