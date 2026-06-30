/** Hiển thị số có hiệu ứng đếm tăng (GSAP). Render sẵn giá trị cuối để an toàn khi reduced-motion. */
import { useRef } from "react";
import { Box, useTheme } from "@mui/material";
import { gsap, useGSAP, reduced } from "../utils/gsap.js";
import { MONO } from "../theme/index.js";

/** @param {{value:number, format:(n:number)=>string}} props */
export default function CountUpValue({ value, format }) {
  const ref = useRef(null);
  const theme = useTheme();

  useGSAP(
    () => {
      if (reduced(theme) || !ref.current) return;
      const obj = { n: 0 };
      gsap.to(obj, {
        n: value,
        duration: 1,
        ease: "power2.out",
        onUpdate: () => {
          if (ref.current) ref.current.textContent = format(obj.n);
        },
      });
    },
    { dependencies: [value] },
  );

  return (
    <Box
      component="span"
      ref={ref}
      sx={{ fontFamily: MONO, fontVariantNumeric: "tabular-nums" }}
    >
      {format(value)}
    </Box>
  );
}
