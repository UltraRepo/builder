import { useState } from "react"

const RooHero = () => {
	const [imagesBaseUri] = useState(() => {
		const w = window as any
		return w.IMAGES_BASE_URI || ""
	})

	return (
		<div className="flex flex-col items-center justify-center pb-4 forced-color-adjust-none">
			<img
				src={`${imagesBaseUri}/icon-dark.svg`}
				alt="AirVeo logo"
				className="h-32"
			/>
		</div>
	)
}

export default RooHero
