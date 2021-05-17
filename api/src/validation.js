const fileType = require('file-type')
const sizeOf = require('image-size')

const maxFileSize = 12*1024*1024
const maxInputPixels = 50000000; // 50 megapixels

const Validation = {
  validateImageData(data) {
    if(data.length > maxFileSize) {
      return { valid: false, code: "file_too_large", message: "File too large", detail: "File exceeds limit of 12MB" };
    }
  
    var file_type = fileType(data);
    if(!file_type) {
      return { valid: false, code: "invalid_file_type", message: "Invalid file type", detail: "Is the given file an image?" };
    }
    if(file_type.ext != "jpg" && file_type.ext != "png") {
      return { valid: false, code: "invalid_file_type", message: "Invalid file type", detail: `Expected jpg/png, received ${file_type.ext}` };
    }
  
    var dimensions = null;
    try {
      dimensions = sizeOf(data);
  
      // switch width/height if EXIF orientation is 5, 6, 7 or 8
      if(dimensions.orientation && dimensions.orientation >= 5 && dimensions.orientation <= 8) {
        var w = dimensions.width;
        dimensions.width = dimensions.height;
        dimensions.height = w;
      }
    }
    catch(e) {
      return { valid: false, code: "invalid_dimensions", message: "Failed to read image dimensions", detail: "The dimensions of the given image could not be read." };
    }
  
    var pixelCount = dimensions.width * dimensions.height;
    if(pixelCount > maxInputPixels) {
      return { valid: false, code: "resolution_too_high", message: "Image resolution too high", detail: `Input image has ${Math.round(pixelCount/1000000)} megapixels, maximum supported input resolution is ${Math.round(maxInputPixels/1000000)} megapixels` };
    }
  
    return { valid: true, width: dimensions.width, height: dimensions.height, ext: file_type.ext };
  }
}

module.exports = Validation
