import React from 'react';
import Link from 'next/link';
import { Box, Typography } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box
      sx={{
        p: 2,
        mt: 'auto',
        textAlign: 'center',
        backgroundColor: 'black',
        color: 'white',
      }}
    >
      <Link href="/" passHref>
        <Box
          component="img"
          src="/logo/plugin-intelligence-logo-white-on-transparent-full.png"
          alt="Plugin Intelligence Logo"
          sx={{ height: 48 }}
        />
      </Link>
      <Box sx={{ mt: 2 }}>
        <Typography variant="body2" sx={{ fontSize: '12px' }}>
          ©Plugin-Intelligence 2024. All rights reserved.
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
          <Link href="/privacy-policy" passHref target="_blank" style={{ fontSize: '12px', color: 'white', textDecoration: 'none' }}>
              Privacy policy
          </Link>
          <Typography variant="body2" sx={{ mx: 1 }}>
            ·
          </Typography>
          <Link href="/terms-of-service" passHref target="_blank" style={{ fontSize: '12px', color: 'white', textDecoration: 'none' }}>
            Terms of service
          </Link>
        </Box>
      </Box>
      <Box sx={{ mt: 2 }}>
        {/*<Link href="https://x.com/peter_csiba" target={"_blank"} passHref style={{ margin: '0 5px', color: 'white', fontSize: '20px' }}>*/}
        {/*  /!*  Twitter Logo *!/*/}
        {/*</Link>*/}
        {/*<Link href="https://www.linkedin.com/in/peter-csiba/" target={"_blank"} passHref style={{ margin: '0 5px', color: 'white', fontSize: '20px' }}>*/}
        {/*    /!*  LinkedIn Logo *!/*/}
        {/*</Link>*/}
      </Box>
    </Box>
  );
};

export default Footer;