import { useState } from "react"

export default function Logo({ width = 100, height = 100 }: { width?: number; height?: number }) {
	const [imagesBaseUri] = useState(() => {
		const w = window as any
		return w.IMAGES_BASE_URI || ""
	})

	return (
		<img
			src={`${imagesBaseUri}/icon-dark.svg`}
			alt="AirVeo logo"
			className="mb-4 mt-4"
			width={width}
			height={height}
		/>
	)
}
