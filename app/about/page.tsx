import { useEffect } from "react";

export const AboutPage = () => {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("animate-slide-in");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 },
    );

    const elements = document.querySelectorAll(".reveal-on-scroll");
    elements.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  return (
    <div className="pt-20">
      {/* Hero Section */}
      <section className="py-24 lg:py-32">
        <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-24">
            <div
              className="lg:col-span-5 reveal-on-scroll"
              style={{ opacity: 0 }}
            >
              <p className="text-label text-gray-400 mb-6">ABOUT US</p>
              <h1 className="heading-xl">
                DESIGN IS NOT JUST WHAT IT LOOKS LIKE.
              </h1>
            </div>
            <div
              className="lg:col-span-7 flex items-end reveal-on-scroll"
              style={{ opacity: 0 }}
            >
              <p className="text-2xl lg:text-3xl font-light leading-relaxed text-gray-600">
                Design is how it works. We believe in objects that serve a
                purpose, that last a lifetime, and that bring joy through their
                simplicity.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Full Width Image */}
      <section className="reveal-on-scroll" style={{ opacity: 0 }}>
        <div className="w-full aspect-[21/9] overflow-hidden">
          <img
            src="/hero.jpg"
            alt="Our showroom"
            className="w-full h-full object-cover"
          />
        </div>
      </section>

      {/* Story Section */}
      <section className="py-24 lg:py-32 border-t border-gray-200">
        <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24">
            <div className="reveal-on-scroll" style={{ opacity: 0 }}>
              <h2 className="heading-md mb-8">Our Story</h2>
              <div className="space-y-6 text-gray-600 leading-relaxed">
                <p>
                  FORME was founded in 2018 with a simple mission: to make
                  exceptional design accessible. We started as a small showroom
                  in Copenhagen, curating a selection of iconic pieces from the
                  mid-century masters alongside contemporary works from emerging
                  designers.
                </p>
                <p>
                  Today, we work directly with manufacturers and designers
                  across Europe and North America, ensuring that every piece in
                  our collection meets our exacting standards for quality,
                  sustainability, and timeless appeal.
                </p>
              </div>
            </div>
            <div className="reveal-on-scroll" style={{ opacity: 0 }}>
              <h2 className="heading-md mb-8">Our Approach</h2>
              <div className="space-y-6 text-gray-600 leading-relaxed">
                <p>
                  We don't follow trends. We select objects that have proven
                  their worth over time, or that show the potential to become
                  classics. Each piece must earn its place in our collection
                  through a combination of functional excellence and aesthetic
                  integrity.
                </p>
                <p>
                  We believe that good design should be lived with, not just
                  looked at. That's why we prioritize comfort, durability, and
                  practicality alongside visual appeal.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Principles Section */}
      <section className="py-24 lg:py-32 bg-[#f5f5f5]">
        <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
          <h2
            className="heading-lg mb-16 reveal-on-scroll"
            style={{ opacity: 0 }}
          >
            OUR PRINCIPLES
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              {
                number: "01",
                title: "Quality First",
                description:
                  "We only work with manufacturers who share our commitment to craftsmanship and materials that stand the test of time.",
              },
              {
                number: "02",
                title: "Sustainable Design",
                description:
                  "We prioritize products made with responsible materials and processes, designed to last generations rather than seasons.",
              },
              {
                number: "03",
                title: "Timeless Appeal",
                description:
                  "We select objects that transcend trends, pieces that will be as relevant in fifty years as they are today.",
              },
            ].map((principle, index) => (
              <div
                key={principle.number}
                className="reveal-on-scroll"
                style={{ opacity: 0, animationDelay: `${(index + 1) * 0.1}s` }}
              >
                <p className="text-label text-gray-400 mb-4">
                  {principle.number}
                </p>
                <h3 className="text-xl font-medium mb-4">{principle.title}</h3>
                <p className="text-gray-500 leading-relaxed">
                  {principle.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team/Image Section */}
      <section className="py-24 lg:py-32">
        <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24 items-center">
            <div className="reveal-on-scroll" style={{ opacity: 0 }}>
              <img
                src="/about.jpg"
                alt="Our design process"
                className="w-full aspect-[3/4] object-cover"
              />
            </div>
            <div className="reveal-on-scroll" style={{ opacity: 0 }}>
              <p className="text-label text-gray-400 mb-6">THE TEAM</p>
              <h2 className="heading-md mb-8">
                A small team with a singular focus.
              </h2>
              <div className="space-y-6 text-gray-600 leading-relaxed">
                <p>
                  Our team consists of designers, architects, and craftspeople
                  who share a passion for exceptional objects. We travel
                  extensively to visit manufacturers, attend design fairs, and
                  discover new talent.
                </p>
                <p>
                  Every member of our team is trained to provide expert
                  guidance, whether you're furnishing an entire home or
                  searching for that one perfect piece.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact CTA */}
      <section className="py-24 lg:py-32 border-t border-gray-200">
        <div className="max-w-[1400px] mx-auto px-6 lg:px-12 text-center">
          <div className="reveal-on-scroll" style={{ opacity: 0 }}>
            <h2 className="heading-lg mb-6">VISIT OUR SHOWROOM</h2>
            <p className="text-gray-500 max-w-xl mx-auto mb-8">
              Experience our collection in person. Our showroom is open by
              appointment, allowing us to give you our full attention.
            </p>
            <div className="space-y-2 text-gray-600">
              <p>123 Design District</p>
              <p>Copenhagen, Denmark 2100</p>
              <p className="pt-4">+45 12 34 56 78</p>
              <p>hello@forme.com</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
