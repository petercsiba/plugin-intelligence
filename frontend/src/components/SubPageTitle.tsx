import React from 'react';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

interface SubPageTitleProps {
  title: string;
}

const SubPageTitle: React.FC<SubPageTitleProps> = ({ title }) => {
  return (
    <Box display="flex" justifyContent="center" mt={6}>
      <Typography variant="h5" component="h2" gutterBottom>
        {title}
      </Typography>
    </Box>
  );
};

export default SubPageTitle;
