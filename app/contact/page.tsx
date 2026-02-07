import { useState, useEffect } from "react";
import { ArrowRight, MapPin, Phone, Mail, Clock } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";

export const ContactPage = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });
  const [showDialog, setShowDialog] = useState(false);

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowDialog(true);
    setFormData({ name: "", email: "", subject: "", message: "" });
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const contactInfo = [
    {
      icon: MapPin,
      label: "Address",
      value: "123 Design District\nCopenhagen, Denmark 2100",
    },
    {
      icon: Phone,
      label: "Phone",
      value: "+45 12 34 56 78",
    },
    {
      icon: Mail,
      label: "Email",
      value: "hello@forme.com",
    },
    {
      icon: Clock,
      label: "Hours",
      value: "Mon–Fri: 10:00–18:00\nSat: By appointment",
    },
  ];

  return (
    <div className="pt-20 min-h-screen">
      {/* Page Header */}
      <section className="py-16 lg:py-24 border-b border-gray-200">
        <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-24">
            <div className="reveal-on-scroll" style={{ opacity: 0 }}>
              <h1 className="heading-xl">CONTACT</h1>
            </div>
            <div
              className="flex items-end reveal-on-scroll"
              style={{ opacity: 0 }}
            >
              <p className="text-gray-500 text-lg leading-relaxed">
                Get in touch for product inquiries, showroom appointments, or
                any questions about our collection.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Content */}
      <section className="py-16 lg:py-24">
        <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-24">
            {/* Left - Contact Info */}
            <div className="lg:col-span-4">
              <div className="lg:sticky lg:top-32 space-y-8">
                {contactInfo.map((item, index) => (
                  <div
                    key={item.label}
                    className="reveal-on-scroll"
                    style={{
                      opacity: 0,
                      animationDelay: `${(index + 1) * 0.1}s`,
                    }}
                  >
                    <div className="flex items-start gap-4">
                      <item.icon size={20} className="text-gray-400 mt-1" />
                      <div>
                        <p className="text-label text-gray-400 mb-2">
                          {item.label}
                        </p>
                        <p className="text-gray-600 whitespace-pre-line">
                          {item.value}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right - Form */}
            <div className="lg:col-span-8">
              <form
                onSubmit={handleSubmit}
                className="space-y-8 reveal-on-scroll"
                style={{ opacity: 0 }}
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <label
                      htmlFor="name"
                      className="text-label text-gray-400 mb-3 block"
                    >
                      NAME
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      className="w-full border-b border-gray-300 py-3 bg-transparent focus:border-black transition-colors"
                      placeholder="Your name"
                    />
                  </div>
                  <div>
                    <label
                      htmlFor="email"
                      className="text-label text-gray-400 mb-3 block"
                    >
                      EMAIL
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="w-full border-b border-gray-300 py-3 bg-transparent focus:border-black transition-colors"
                      placeholder="your@email.com"
                    />
                  </div>
                </div>

                <div>
                  <label
                    htmlFor="subject"
                    className="text-label text-gray-400 mb-3 block"
                  >
                    SUBJECT
                  </label>
                  <select
                    id="subject"
                    name="subject"
                    value={formData.subject}
                    onChange={handleChange}
                    required
                    className="w-full border-b border-gray-300 py-3 bg-transparent focus:border-black transition-colors appearance-none cursor-pointer"
                  >
                    <option value="">Select a subject</option>
                    <option value="inquiry">Product Inquiry</option>
                    <option value="appointment">Showroom Appointment</option>
                    <option value="quote">Request Quote</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="message"
                    className="text-label text-gray-400 mb-3 block"
                  >
                    MESSAGE
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    required
                    rows={6}
                    className="w-full border-b border-gray-300 py-3 bg-transparent focus:border-black transition-colors resize-none"
                    placeholder="Tell us about your inquiry..."
                  />
                </div>

                <div className="pt-4">
                  <button
                    type="submit"
                    className="inline-flex items-center gap-3 bg-black text-white px-8 py-4 text-label hover:bg-gray-800 transition-colors"
                  >
                    SEND MESSAGE
                    <ArrowRight size={16} />
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Map Placeholder */}
      <section className="border-t border-gray-200">
        <div className="w-full aspect-[21/9] bg-[#f5f5f5] flex items-center justify-center">
          <div className="text-center">
            <MapPin size={32} className="mx-auto mb-4 text-gray-400" />
            <p className="text-gray-500">123 Design District, Copenhagen</p>
          </div>
        </div>
      </section>

      {/* Success Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-xl font-medium">
              Message Sent
            </DialogTitle>
            <DialogDescription className="text-gray-500 pt-2">
              Thank you for reaching out. We have received your message and will
              get back to you within 24 hours.
            </DialogDescription>
          </DialogHeader>
          <div className="pt-4">
            <button
              onClick={() => setShowDialog(false)}
              className="w-full bg-black text-white py-3 text-label hover:bg-gray-800 transition-colors"
            >
              CLOSE
            </button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};
