import {PluginTimeseriesData, TopPluginResponse} from "./models";
import {MarketplaceName} from "../marketplaces/models";

const baseUrl = process.env.NEXT_PUBLIC_API_URL

export const fetchTopPlugins = async (marketplace_name: MarketplaceName): Promise<TopPluginResponse[]> => {
    const url = `${baseUrl}/plugins/top?marketplace_name=${marketplace_name}`
    console.log("Attempting to fetch plugins from", url);
    const response = await fetch(url);
    return await response.json();
};

export const fetchCompanyPlugins = async (companySlug: string): Promise<TopPluginResponse[]> => {
    const url = `${baseUrl}/plugins/company/${companySlug}`
    console.log("Attempting to fetch plugins from", url);
    const response = await fetch(url);
    return await response.json();
};

export const fetchPluginTimeseries = async (pluginId: string): Promise<PluginTimeseriesData[]> => {
    const url = `${baseUrl}/charts/plugins-timeseries/${pluginId}`
    console.log("Attempting to fetch plugin timeseries data from", url);
    const response = await fetch(url);
    return await response.json();
};
