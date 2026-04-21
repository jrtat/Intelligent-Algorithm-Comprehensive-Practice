from processor.tools.Matcher import Matcher
from processor.utils.FileProcessor import FileProcessor

if __name__ == "__main__":

    fp_resume = FileProcessor("../temp/resume_Mike_20260416_232131.json")
    resume_info = fp_resume.read()

    matcher = Matcher(resume_info)
    matcher.get_jobs()