import React from 'react';
import Rating from '@mui/material/Rating';
import Box from '@mui/material/Box';

interface RatingStarsWithTextProps {
  rating?: number | null;
}

const RatingStarsWithText: React.FC<RatingStarsWithTextProps> = ({ rating }) => {
  return (
    <Box display="flex" alignItems="center">
      <Rating
        name="company-weighted-avg-rating"
        value={rating ?? 0}
        precision={0.25}
        readOnly
      />
      <Box ml={2}>
        {rating !== null && rating !== undefined ? rating : "No Ratings"}
      </Box>
    </Box>
  );
};

export default RatingStarsWithText;
