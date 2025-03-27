## Color Spaces Mapping
RGB, CMYK, Grayscale color spaces are primary, standard and wirespread used in digital media. However, the documents using other color spaces or custom-defined schemes will not be supported or mapped into wrong hex color

## File Processing
- PDF files contain various content streams according to different aspects such as fonts, images, or page sizes. These streams often carry encoded color information in some certain formats(e.g., binary data). The 'latin-1' will be used to encode for general cases, so we can use this for decoding the bianry datta. For all the streams can not be directly decoded by 'latin-1', we will use zlib to decompress.
- Once potential color values are extracted from the streams, they need to be matched against predefined patterns for each color space. Extracted components are converted into RGB format using converter functions associated with each color space. This will make sure the consistent representation and comparision of colors across diffrent spaces.
- By tracking the count of occurrences for each color instance, we will summerize the usage statistics, which are essential for analyzing color distribution within the document.
