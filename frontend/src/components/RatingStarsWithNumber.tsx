import React from 'react';
import Rating from '@mui/material/Rating';
import Box from '@mui/material/Box';
import {formatNumber, formatNumberShort} from "@/utils";

interface RatingStarsWithTextProps {
  rating?: number | null;
  ratingCount?: number | null;
}

const RatingStarsWithText: React.FC<RatingStarsWithTextProps> = ({ rating, ratingCount }) => {
  return (
    <Box display="flex" alignItems="center">
      <Rating
        name="company-weighted-avg-rating"
        value={rating ?? 0}
        precision={0.25}
        readOnly
      />
      <Box ml={2}>
        {rating ? <strong>{formatNumber(rating)}</strong> : "No Ratings"}
        {ratingCount ? ` (out of ${formatNumberShort(ratingCount)} ratings)` : ""}
      </Box>
    </Box>
  );
};

export default RatingStarsWithText;
