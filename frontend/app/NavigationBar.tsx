"use client";

import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Link from 'next/link';
import {Box, Icon, styled } from '@mui/material';


const NavigationBar = () => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Styled Link component to remove default styles
  const StyledLink = styled(Link)({
    textDecoration: 'none',
    color: 'inherit',
  });

  return (
    <AppBar position="static" sx={{ backgroundColor: 'black' }}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            <Link href="/" passHref>
              <Box
                component="img"
                src="/logo/plugin-intelligence-logo-white-on-transparent-full.png"
                alt="Plugin Intelligence Logo"
                sx={{ height: 48 }}
              />
            </Link>
        </Typography>
        {/*TODO: Change after we have a proper landing page */}
        <StyledLink href="/" passHref>
            <Button color="inherit">
                  <Box
                    component="img"
                    src="/icons/google-workspace-logo.png"
                    alt="Google Workspace Marketplace Logo"
                    sx={{ mr: 0.5, width: 16, height: 16 }}
                  />
              Google Workspace
            </Button>
        </StyledLink>
        <StyledLink href="/marketplaces/chrome_extensions" passHref>
            <Button color="inherit">
              <Box
                component="img"
                src="/icons/chrome-webstore-logo.svg"
                alt="Chrome Extensions Web Store Logo"
                sx={{ mr: 0.5, width: 16, height: 16 }}
              />
          Chrome Extensions
            </Button>
        </StyledLink>
        {/*<Button color="inherit">Salesforce AppExchange</Button>*/}
        <Button color="inherit" onClick={handleMenuClick}>
          More
              <Box
                component="img"
                src="/icons/premium-feature-icon-crown.png"
                alt="Premium Feature"
                sx={{ ml: 0.5, width: 16, height: 16 }}
              />
        </Button>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
        <StyledLink href="/pricing" passHref>
          <MenuItem onClick={handleMenuClose}>
              <Box
                component="img"
                src="/icons/wordpress-logo.svg"
                alt="Wordpress Plugins Logo"
                sx={{ mr: 0.5, width: 16, height: 16 }}
              />
              Wordpress Plugins
          </MenuItem>
       </StyledLink>
        <StyledLink href="/pricing" passHref>
          <MenuItem onClick={handleMenuClose}>
              <Box
                component="img"
                src="/icons/shopify-app-store-logo.svg"
                alt="Shopify App Store Logo"
                sx={{ mr: 0.5, width: 16, height: 16 }}
              />
              Shopify App Store
          </MenuItem>
       </StyledLink>
        <StyledLink href="/pricing" passHref>
          <MenuItem onClick={handleMenuClose}>
              <Box
                component="img"
                src="/icons/salesforce-logo-square-64px.png"
                alt="Salesforce App Exchange Logo"
                sx={{ mr: 0.5, width: 16, height: 16 }}
              />
            Salesforce App Exchange
          </MenuItem>
       </StyledLink>
        <StyledLink href="/pricing" passHref>
          {/*  https://monday.com/marketplace*/}
           <MenuItem onClick={handleMenuClose}>
              <Box
                component="img"
                src="/icons/monday-logo.png"
                alt="Monday App Marketplace Logo"
                sx={{ mr: 0.5, width: 16, height: 16 }}
              />
              Monday App Marketplace
            </MenuItem>
          </StyledLink>
        </Menu>
        <StyledLink href="/pricing" passHref>
          <Button color="inherit">Pricing</Button>
        </StyledLink>
        <Link href="/pricing" passHref>
            <Button variant="contained" sx={{ backgroundColor: 'yellowgreen', color: 'black' }}>
                Connect Data
              <Box
                component="img"
                src="/icons/microsoft-excel-logo.svg"
                alt="Microsoft Excel Logo"
                sx={{ ml: 0.5, width: 16, height: 16 }}
              />
              <Box
                component="img"
                src="/icons/snowflake-logo.svg"
                alt="Snowflake Logo"
                sx={{ ml: 0.5, height: 16 }}
              />
              <Box
                component="img"
                src="/icons/sigma-logo.jpg"
                alt="Sigma Logo"
                sx={{ ml: 0.5, width: 16, height: 16 }}
              />
            </Button>
        </Link>
      </Toolbar>
    </AppBar>
  );
};

export default NavigationBar;
