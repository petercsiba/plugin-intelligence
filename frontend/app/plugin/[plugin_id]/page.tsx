import React from "react";
import NextLink from "next/link";
import {
    Button,
    Container,
    Paper,
    Rating,
    Typography,
    List,
    ListItem,
    ListItemText,
    Divider,
} from "@mui/material";
import Box from "@mui/material/Box";
import {PluginDetailsResponse} from "../models";
import ExternalLink from "@/components/ExternalLink";
import {formatCurrency, formatNumber} from "@/utils";

const baseUrl = process.env.NEXT_PUBLIC_API_URL

// Function to fetch plugin details
async function fetchPluginDetails(plugin_id: string): Promise<PluginDetailsResponse | null> {
    const response = await fetch(`${baseUrl}/plugin/${plugin_id}/details`, {
        cache: "no-store", // Adjust caching as needed
    });

    if (!response.ok) {
        console.error(`Error fetching plugin details: ${response.statusText}`);
        return null;
    }

    return await response.json();
}

export default async function PluginDetailsPage({ params }: { params: { plugin_id: string } }) {
    const plugin = await fetchPluginDetails(params.plugin_id);
    if (!plugin) {
        return (
            <div>
                <p>Oops! Something went wrong. Please try again later or go back to the main page.</p>
                <NextLink href="/">
                    <Button variant="contained" color="primary">
                        Back to Main Page
                    </Button>
                </NextLink>
            </div>
        );
    }

    // Format ranges
    const revenueRange = plugin && plugin.revenue_lower_bound && plugin.revenue_upper_bound
        ? `${formatCurrency(plugin.revenue_lower_bound)} - ${formatCurrency(plugin.revenue_upper_bound)}`
        : "N/A";

    // Convert comma-separated lists
    const mainIntegrations = plugin && plugin.main_integrations ? plugin.main_integrations.split(",").join(", ") : "N/A";
    const searchTerms = plugin && plugin.search_terms ? plugin.search_terms.split(",").join(", ") : "N/A";
    const tags = plugin && plugin.tags ? plugin.tags.split(",").join(", ") : "N/A";

    return (
        <Container maxWidth="md">
            <Paper elevation={3} style={{ padding: "2em", marginTop: "2em" }}>
                <Typography variant="h4" gutterBottom>
                    {plugin.name} ({plugin.marketplace_name})
                </Typography>
                <Box display="flex" alignItems="center" gap={2} mt={2}>
                    <Typography variant="body1">
                        {plugin.user_count ? `${formatNumber(plugin.user_count)} Users` : "N/A"}
                    </Typography>
                    <Rating
                        name="plugin-rating"
                        value={plugin.rating ? parseFloat(plugin.rating) : 0}
                        precision={0.25}
                        readOnly
                    />
                    <Typography variant="body2">
                        {plugin.rating_count ? `${plugin.rating_count.toLocaleString()} Ratings` : "N/A"}
                    </Typography>
                </Box>
                <List>
                    <ListItem>
                        <ListItemText
                            primary="Marketplace ID"
                            secondary={plugin.marketplace_id || "N/A"}
                        />
                        <ListItemText
                            primary={`See on ${plugin.marketplace_name} Marketplace`}
                            secondary={
                                <ExternalLink
                                    href={plugin.marketplace_link || "#"}
                                >
                                    Link
                                </ExternalLink>
                            }
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Revenue Estimate" secondary={revenueRange} />
                        <ListItemText
                            primary="Pricing Tiers"
                            secondary={
                                <Box display="flex" alignItems="center" flexWrap="wrap">
                                    {plugin.pricing_tiers?.map((tier, index, array) => (
                                        <React.Fragment key={index}>
                                            <Typography variant="body2">{tier}</Typography>
                                            {index < array.length - 1 && <Divider orientation="vertical" flexItem style={{ margin: '0 8px' }} />}
                                        </React.Fragment>
                                    )) || <Typography variant="body2">Unknown</Typography>}
                                </Box>
                            }
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Main Integrations" secondary={mainIntegrations} />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Search Terms" secondary={searchTerms} />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Tags" secondary={tags} />
                    </ListItem>
                </List>

                {/* Blog-style Content */}

                {plugin.elevator_pitch ? (
                    <Box mt={4}>
                        <Typography variant="h5">Elevator Pitch</Typography>
                        <Typography paragraph>{plugin.elevator_pitch || "N/A"}</Typography>
                    </Box>
                ) : null}
                <Box mt={4}>
                    <Typography variant="h5">Overview Summary</Typography>
                    <Typography paragraph>{plugin.overview_summary || "N/A"}</Typography>
                </Box>
                {plugin.revenue_analysis_html ? (
                    <Box mt={4}>
                        <Typography variant="h5">Full Text Analysis</Typography>
                        <Typography paragraph dangerouslySetInnerHTML={{__html: plugin.revenue_analysis_html}}>
                        </Typography>
                    </Box>
                ):null}
            </Paper>
        </Container>
    );
}
